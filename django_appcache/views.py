import os

from django import http
from django.views.decorators.cache import cache_page

from . import settings


# Cache for 5 minutes to ease server load but keep deploys snappy.
@cache_page(60 * 5)
def manifest(request):
    if not os.path.exists(settings.APPCACHE_FILE_PATH):
        return http.HttpResponseNotFound()
    with open(settings.APPCACHE_FILE_PATH, 'r') as fp:
        return http.HttpResponse(fp.read(),
                                 content_type='text/cache-manifest')
