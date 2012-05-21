from datetime import datetime
from glob import glob
import os
import posixpath

from django.core.management.base import BaseCommand, CommandError
from django.template import Context, loader

from django_appcache import settings


class Command(BaseCommand):
    help = 'Build a new appcache manifest file'

    def handle(self, *args, **options):
        cache_paths = []
        for part in settings.APPCACHE_MEDIA_TO_CACHE:
            pt = posixpath.join(settings.MEDIA_ROOT, part)
            for pt in glob(pt):
                if not os.path.exists(pt):
                    raise CommandError('MEDIA_ROOT path %r does not exist at '
                                       '%r' % (part, pt))
                pt = pt.replace(settings.MEDIA_ROOT, settings.MEDIA_URL)
                pt = pt.replace('//', '/')
                cache_paths.append(pt)

        cache_paths.extend(settings.APPCACHE_TO_CACHE)
        cache_paths = "\n".join(cache_paths)
        network_paths = "\n".join(settings.APPCACHE_NET_PATHS)
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
