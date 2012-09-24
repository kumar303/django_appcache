import os
import shutil
import tempfile

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase

import mock
from nose.tools import raises

from django_appcache.management.commands.build_appcache import Command
from django_appcache import settings


class _Case(TestCase):

    def setUp(self):
        fp = tempfile.NamedTemporaryFile('w', delete=False)
        fp.close()
        self.addCleanup(lambda: os.unlink(fp.name))
        self.tmp = fp.name

    def tearDown(self):
        cache.clear()


class Test(_Case):

    def test_build(self):
        with mock.patch.object(settings, 'APPCACHE_FILE_PATH', self.tmp):
            Command().handle()
            assert os.path.exists(settings.APPCACHE_FILE_PATH)
            with open(settings.APPCACHE_FILE_PATH, 'r') as fp:
                mf = fp.read()
            assert 'CACHE MANIFEST' in mf

    def test_serve(self):
        with mock.patch.object(settings, 'APPCACHE_FILE_PATH', self.tmp):
            Command().handle()
            res = self.client.get(reverse('django_appcache.manifest'))
            self.assertContains(res, 'CACHE MANIFEST')

    def test_missing_manifest(self):
        with mock.patch.object(settings, 'APPCACHE_FILE_PATH',
                               '__bogus__/manifest.appcache'):
            res = self.client.get(reverse('django_appcache.manifest'))
            self.assertEquals(res.status_code, 404)



class TestMedia(_Case):

    def setUp(self):
        super(TestMedia, self).setUp()
        self.media_tmp = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.media_tmp))
        with open(os.path.join(self.media_tmp, 'somefile.css'), 'w') as fp:
            fp.write('<css>')
        self.patches = [
            mock.patch.object(settings, 'APPCACHE_FILE_PATH', self.tmp),
            mock.patch.object(settings, 'MEDIA_ROOT', self.media_tmp)
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        super(TestMedia, self).tearDown()
        for p in self.patches:
            p.stop()

    @mock.patch.object(settings, 'APPCACHE_MEDIA_TO_CACHE',
                       ['somefile.css'])
    def test_media(self):
        Command().handle()
        res = self.client.get(reverse('django_appcache.manifest'))
        self.assertContains(res, 'somefile.css')

    @mock.patch.object(settings, 'APPCACHE_MEDIA_TO_CACHE',
                       ['somefile.css'])
    def test_media_url(self):
        with mock.patch.object(settings, 'MEDIA_URL', 'https://cdn/'):
            Command().handle()
        res = self.client.get(reverse('django_appcache.manifest'))
        self.assertContains(res, 'https://cdn/somefile.css')

    @mock.patch.object(settings, 'APPCACHE_MEDIA_TO_CACHE',
                       ['somefile.css?cache_id=123'])
    def test_media_url_with_qs(self):
        Command().handle()
        res = self.client.get(reverse('django_appcache.manifest'))
        self.assertContains(res, 'somefile.css?cache_id=123')

    @mock.patch.object(settings, 'APPCACHE_MEDIA_TO_CACHE',
                       ['http://cdn-url/somefile.css?cache_id=123'])
    @raises(ValueError)
    def test_media_url_cannot_have_domains(self):
        Command().handle()

    def test_callable_media_paths(self):

        def make_paths():
            return ['somefile.css']

        with mock.patch.object(settings, 'APPCACHE_MEDIA_TO_CACHE',
                               make_paths):
            Command().handle()
        res = self.client.get(reverse('django_appcache.manifest'))
        self.assertContains(res, 'somefile.css')

    def test_callable_paths(self):

        def make_paths():
            return ['http://cdn/somefile.css']

        with mock.patch.object(settings, 'APPCACHE_TO_CACHE',
                               make_paths):
            Command().handle()
        res = self.client.get(reverse('django_appcache.manifest'))
        self.assertContains(res, 'http://cdn/somefile.css')

    def test_callable_net_paths(self):

        def make_paths():
            return ['http://external-cdn/somefile.css']

        with mock.patch.object(settings, 'APPCACHE_NET_PATHS',
                               make_paths):
            Command().handle()
        res = self.client.get(reverse('django_appcache.manifest'))
        self.assertContains(res, 'http://external-cdn/somefile.css')
