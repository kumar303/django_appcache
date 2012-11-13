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
        cache_paths = []  # URL paths.
        abs_cache_paths = []  # Absolute file paths.

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
                abs_cache_paths.append(os.path.abspath(pt))
                pt = media_path_to_url(pt)
                if parsed.query:
                    pt = u'%s?%s' % (pt, parsed.query)
                cache_paths.append(pt)

        cache_paths.extend(_iter_setting(settings.APPCACHE_TO_CACHE))
        cache_paths.extend(extract_images(abs_cache_paths))
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
    """
    Scans list of files for css files. Opens each css file then
    extracts image paths within url() declarations for caching.

    Returns a unique set of image URLs to cache.
    """
    images = []

    for css_path in files:
        if not css_path.endswith('.css'):
            continue
        with open(css_path, 'r') as css_in:
            css_content = css_in.read()
        # Look for all url() declarations within the CSS rules.
        imgs = re.findall(r'''url\(['"]?([^\)'"]+)['"]?\)''', css_content)
        css_dir = os.path.dirname(css_path)
        if imgs:
            for img in imgs:
                if img.lower().startswith('http'):
                    # External image to cache.
                    images.append(img)
                    continue
                parts = img.split('?')
                img = parts[0]
                query = parts[1] if len(parts) > 1 else None
                path = os.path.normpath(os.path.join(css_dir, img))
                if not os.path.exists(path):
                    raise ValueError('image %r in CSS file %r does not '
                                     'exist at %r' % (img, css_path, path))
                url = media_path_to_url(path)
                if query:
                    url = '%s?%s' % (url, query)
                images.append(url)

    return set(images)


def media_path_to_url(path):
    """
    Convert a file path on MEDIA_ROOT to a URL using MEDIA_URL
    """
    media_url = settings.MEDIA_URL
    if media_url.endswith('/'):
        media_url = media_url[:-1]
    return path.replace(settings.MEDIA_ROOT, media_url)


def _iter_setting(setting):
    if callable(setting):
        setting = setting()
    for val in setting:
        yield val
