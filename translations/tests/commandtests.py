from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import unittest

import pkg_resources

from translations import commands


class AppNameTest(unittest.TestCase):

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
