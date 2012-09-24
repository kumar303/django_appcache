django_appcache helps you build and serve an
[appcache](https://developer.mozilla.org/en/Using_Application_Cache)
manifest from [Django](https://www.djangoproject.com/).

Here's a good [guide](http://www.html5rocks.com/en/tutorials/appcache/beginner/)
to understanding how the appcache works.

An appcache manifest is a standard file that web browsers will use to let people
continue using your application when offline. It's useful for mobile
or if you're building an [open web app](https://developer.mozilla.org/en/Apps)
that will be installed on a device from a website (like a
[Boot To Gecko](https://developer.mozilla.org/en/Mozilla/Boot_to_Gecko/Writing_a_web_app)
app).

Installation
============

Install it like this in your settings.py file:

    INSTALLED_APPS = [
        'django_appcache',
    ]

Usage
=====

All files listed in the default or cache section of the
manifest will be cached *indefinitely* or until your manifest file changes. The
first thing you'll need to do is incorporate this command into your deploy
process:

    ./manage.py build_appcache

This creates a new appcache file and puts a timestamp on it to invalidate your
cached files each time you deploy. To serve the manifest, add this to your
urls.py or serve the generated file from a CDN or wherever.

    urlpatterns = patterns('',
        url('^appcache/', include('django_appcache.urls')),
    )

This view is cached for 5 minutes.
To tell the browser to use the appcache, link to it like this:

    {% load django_appcache_tags %}
    <html {% appcache_manifest_link|safe %} >

This will add an attribute to the html tag like this: ``manifest="<url>"``.
Alternatively, if you have [jingo](https://github.com/jbalogh/jingo/)
installed for use with Jinja2 then you can call the function
``appcache_manifest_link()`` in your templates.

**IMPORTANT**: Every page you serve that links to the appcache will
be cached itself. You probably don't want to do this on forms or any page
that might
update dynamically. If the index page of your app cannot be cached like this
then you probably don't want to use an appcache at all. If you still think you
do then consider updating your index page using JavaScript.

Settings
========

Here are some settings you can use to customize the appcache.

APPCACHE_MEDIA_TO_CACHE
-----------------------

These are paths relative to your MEDIA_ROOT that you want to explicitly cache.
The browser will load *all* of these URLs when your app first loads
so be mindful to only list essential media files. The actual URL of the path
to cache will be determined using MEDIA_URL.
If you use wildcards here the real paths to the file(s) will be
expanded using ``glob.glob()``. Example:

    APPCACHE_MEDIA_TO_CACHE = [
        'css/all-compressed.css',
        'js/all-compressed.js?cache_id=123',
        'js/lib/jquery-1.*.js'
    ]

In this example, a manifest would include cache entries looking something like
this:

    CACHE:
    http://media-url/media/css/all-compressed.css
    http://media-url/media/js/all-compressed.js?cache_id=123
    http://media-url/media/js/lib/jquery-1.6.4.js
    http://media-url/media/js/lib/jquery-1.7.1.js

Notice how the wildcard ``jquery-*.js`` was expanded to actual paths. This
follows Python glob syntax.

This setting can also be a callable object that yields paths when
iterated over.

APPCACHE_TO_CACHE
-----------------

These are absolute paths to add to the cache. Wildcards are not allowed here.
These paths will be added as-is to the cache section.
Example:

    APPCACHE_TO_CACHE = [
        '/favicon.ico',
        'https://some-server.net/include.js'
    ]

This setting can also be a callable object that yields paths when
iterated over.

APPCACHE_NET_PATHS
------------------

These are absolute paths (or wildcards) to require network access for.
By default, all paths (*) will hit the network unless they were listed
in the cache section. The default looks like this:

    APPCACHE_NET_PATHS = ['*']

This setting can also be a callable object that yields paths when
iterated over.

APPCACHE_FALLBACK_PATHS
-----------------------

This is a dict mapping requested paths to fallback paths that will be
used when the app is offline. Example:

    APPCACHE_FALLBACK_PATHS = {
        '/user-icons/': '/offline-icon.png',  # map a directory to a single URL.
        '/': '/offline.html',  # map all requests to a cached offline page.
    }

APPCACHE_TEMPLATE
-----------------

This is the template path to load when building an appcache manifest.
You only need to override this if you're using a custom template.

APPCACHE_FILE_PATH
------------------

The path on your local disk where the built appcache manifest should be saved
to. By default it will be written to your MEDIA_ROOT directory as a file named
manifest.appcache.

APPCACHE_URL
------------

The URL that will serve your appcache manifest.
By default this is None, which will let django_appcache serve it for you.

Developers
==========

To run the tests, install [tox](http://tox.testrun.org/latest/)
then type this from the root:

    tox
