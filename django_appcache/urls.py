from django.conf.urls.defaults import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^manifest.appcache$', views.manifest,
        name='django_appcache.manifest'),
)
