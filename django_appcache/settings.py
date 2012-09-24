import os
from django.conf import settings as base_settings

# These are paths relative to your MEDIA_ROOT that you want to explicitly
# cache. The browser will load *all* of these URLs when your app first loads
# so be mindful to only list essential media files. The actual URL of the path
# to cache will be determined using MEDIA_URL.
# If you use wildcards here the real paths to the file(s) will be
# expanded using glob.glob(). This can be a list of paths or it can be a
# callable object that yields paths when iterated over.
APPCACHE_MEDIA_TO_CACHE = []

# These are absolute paths to add to the cache. Wildcards are not allowed here.
# These paths will be added as-is to the cache section.
# For example, you might include http://otherserver.net/include.js here.
# This can be a list of paths or it can be a
# callable object that yields paths when iterated over.
APPCACHE_TO_CACHE = []

# These are absolute paths (or wildcards) to require network access for.
# By default, all paths (*) will hit the network unless they were listed
# in the cache section.
# This can be a list of paths or it can be a
# callable object that yields paths when iterated over.
APPCACHE_NET_PATHS = ['*']

# This is a dict mapping keys (requested path) to fallback paths that will be
# used when the app is offline.
APPCACHE_FALLBACK_PATHS = {}

# Template path to load when building an appcache manifest.
APPCACHE_TEMPLATE = 'django_appcache/manifest.appcache'

# The path on your local disk where the built appcache manifest should be saved
# to.
APPCACHE_FILE_PATH = os.path.join(base_settings.MEDIA_ROOT,
                                  'manifest.appcache')

# The URL that will serve your appcache manifest.
# By default this is None, which will let django_appcache serve it for you.
APPCACHE_URL = None

# Apply custom settings.
for name in dir(base_settings):
    locals()[name] = getattr(base_settings, name)
