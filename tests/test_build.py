import os
import shutil
import tempfile

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase

import mock

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


@mock.patch.object(settings, 'APPCACHE_MEDIA_TO_CACHE',
                   ['somefile.css'])
class TestMedia(_Case):

    def setUp(self):
        super(TestMedia, self).setUp()
        self.media_tmp = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.media_tmp))
        with open(os.path.join(self.media_tmp, 'somefile.css'), 'w') as fp:
            fp.write('<css>')

    def test_media(self):
        with mock.patch.object(settings, 'APPCACHE_FILE_PATH', self.tmp):
            with mock.patch.object(settings, 'MEDIA_ROOT', self.media_tmp):
                Command().handle()
            res = self.client.get(reverse('django_appcache.manifest'))
            self.assertContains(res, 'somefile.css')

    def test_media_url(self):
        with mock.patch.object(settings, 'APPCACHE_FILE_PATH', self.tmp):
            with mock.patch.object(settings, 'MEDIA_ROOT', self.media_tmp):
                with mock.patch.object(settings, 'MEDIA_URL', 'https://cdn/'):
                    Command().handle()
            res = self.client.get(reverse('django_appcache.manifest'))
            self.assertContains(res, 'https://cdn/somefile.css')
