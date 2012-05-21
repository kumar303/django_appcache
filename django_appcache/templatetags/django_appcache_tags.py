from django import template
from django.core.urlresolvers import reverse

try:
    import jingo
    jingo_register_fn = jingo.register.function
except ImportError:
    jingo_register_fn = lambda fn: fn

from django_appcache import settings

register = template.Library()


@register.simple_tag
@jingo_register_fn
def appcache_manifest_link():
    if settings.APPCACHE_URL:
        manifest_url = settings.APPCACHE_URL
    else:
        manifest_url = reverse('django_appcache.manifest')
    return 'manifest="%s"' % manifest_url
