import os
import shutil
import tempfile

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase

import mock

from django_appcache.management.commands.build_appcache import Command
from django_appcache import settings


class Test(TestCase):

    def setUp(self):
        fp = tempfile.NamedTemporaryFile('w', delete=False)
        fp.close()
        self.addCleanup(lambda: os.unlink(fp.name))
        self.tmp = fp.name

    def tearDown(self):
        cache.clear()

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

    @mock.patch.object(settings, 'APPCACHE_MEDIA_TO_CACHE',
                       ['somefile.css'])
    def test_media(self):
        media_tmp = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(media_tmp))
        with open(os.path.join(media_tmp, 'somefile.css'), 'w') as fp:
            fp.write('<css>')
        with mock.patch.object(settings, 'APPCACHE_FILE_PATH', self.tmp):
            with mock.patch.object(settings, 'MEDIA_ROOT', media_tmp):
                Command().handle()
            res = self.client.get(reverse('django_appcache.manifest'))
            self.assertContains(res, 'somefile.css')

    def test_missing_manifest(self):
        with mock.patch.object(settings, 'APPCACHE_FILE_PATH',
                               '__bogus__/manifest.appcache'):
            res = self.client.get(reverse('django_appcache.manifest'))
            self.assertEquals(res.status_code, 404)
