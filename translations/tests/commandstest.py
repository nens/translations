from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import unittest

import mock
import pkg_resources

from translations import commands


class SetupConfigTest(unittest.TestCase):

    def test_no_section(self):
        # Test on ourselves.
        setup_config = commands.SetupConfig()
        self.assertRaises(Exception, setup_config.app_name, 'translations')

    def test_with_section(self):
        # Test on ourselves.
        config_filename = pkg_resources.resource_filename(
            'translations.tests', 'setup_with_sections.cfg')
        setup_config = commands.SetupConfig(config_filename=config_filename)
        self.assertEquals(setup_config.app_name(), 'tralalalations')


class CommandsTest(unittest.TestCase):

    def test_get_app_name1(self):
        # Test on ourselves.
        self.assertEquals(commands._get_app_name(), 'translations')

    def test_get_app_dir1(self):
        # Test on ourselves.
        our_dir = pkg_resources.resource_filename('translations', '')
        self.assertEquals(commands._get_app_dir(), our_dir)

    @mock.patch('subprocess.call')
    def test_upload_source_language_catalog(self, patched_call):
        commands.upload_source_language_catalog()
        self.assertTrue(patched_call.called())
