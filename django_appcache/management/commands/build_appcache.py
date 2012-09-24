from datetime import datetime
from glob import glob
import os
import posixpath
from urlparse import urlparse

from django.core.management.base import BaseCommand, CommandError
from django.template import Context, loader

from django_appcache import settings


class Command(BaseCommand):
    help = 'Build a new appcache manifest file'

    def handle(self, *args, **options):
        cache_paths = []
        media_url = settings.MEDIA_URL
        if media_url.endswith('/'):
            media_url = media_url[:-1]

        for part in _iter_setting(settings.APPCACHE_MEDIA_TO_CACHE):
            parsed = urlparse(part)  # remove query string
            if parsed.netloc:
                raise ValueError('You cannot specify absolute URLs '
                                 'in APPCACHE_MEDIA_TO_CACHE. Use '
                                 'APPCACHE_TO_CACHE instead.')
            pt = posixpath.join(settings.MEDIA_ROOT, parsed.path)
            for pt in glob(pt):
                if not os.path.exists(pt):
                    raise CommandError('MEDIA_ROOT path %r does not exist at '
                                       '%r' % (parsed.path, pt))
                pt = pt.replace(settings.MEDIA_ROOT, media_url)
                if parsed.query:
                    pt = u'%s?%s' % (pt, parsed.query)
                cache_paths.append(pt)

        cache_paths.extend(_iter_setting(settings.APPCACHE_TO_CACHE))
        cache_paths = "\n".join(cache_paths)
        network_paths = "\n".join(_iter_setting(settings.APPCACHE_NET_PATHS))
        fallback_paths = "\n".join(['%s %s' % (op, fp) for op, fp in
                                    settings.APPCACHE_FALLBACK_PATHS.items()])

        vr = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S+0000')
        ctx = Context({'build_version': vr,
                       'settings': settings,
                       'cache_paths': cache_paths,
                       'network_paths': network_paths,
                       'fallback_paths': fallback_paths})
        tpl = loader.get_template(settings.APPCACHE_TEMPLATE)
        with open(settings.APPCACHE_FILE_PATH, 'w') as fp:
            fp.write(tpl.render(ctx))
        print 'Wrote appcache to %s' % fp.name


def _iter_setting(setting):
    if callable(setting):
        setting = setting()
    for val in setting:
        yield val
