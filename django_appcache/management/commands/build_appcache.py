from datetime import datetime
from glob import glob
import os
import posixpath
import re
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
        cache_paths.extend(extract_images(cache_paths))
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


def extract_images(files):
    images = []
    css_files = [f for f in files if f.split('?')[0].endswith('.css')]

    for css_path in css_files:
        css_path = css_path.split('?')[0]
        if css_path.startswith('/'):
            css_path = css_path[1:]
        css_content = ''
        with open(css_path, 'r') as css_in:
            css_content = css_in.read()
        imgs = re.findall('url\(([^)]*?)\)', css_content)
        if imgs:
            for img in imgs:
                url = os.path.normpath(os.path.join('/',
                    os.path.dirname(css_path),
                    img))
                images.append(url)

    return unique(images)


# Thanks peterbe!
def unique(seq):
   set = {}
   map(set.__setitem__, seq, [])
   return set.keys()


def _iter_setting(setting):
    if callable(setting):
        setting = setting()
    for val in setting:
        yield val
