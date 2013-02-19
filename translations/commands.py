#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from optparse import OptionParser
import os
from subprocess import call, Popen, PIPE
import sys

from ConfigParser import ConfigParser, NoSectionError, NoOptionError

from django.core.management import call_command


logger = logging.getLogger(__name__)


SETUP_CONFIG_FILE = 'setup.cfg'
TX_CMD = 'tx'  # needs buildout >= 2.0.1


class SetupConfig(object):
    """Wrapper around the setup.cfg file if available.

    Mostly, this is here to get app name fro translations from setup.cfg:

    [translations]
    app_name = lizard_ui

    """

    def __init__(self, config_filename=SETUP_CONFIG_FILE):
        """Grab the configuration (overridable for test purposes)"""
        # If there is a setup.cfg in the package, parse it
        self.config_filename = config_filename
        if not os.path.exists(self.config_filename):
            self.config = None
            return
        self.config = ConfigParser()
        self.config.read(self.config_filename)

    def app_name(self):
        """Return app_name from setup.cfg

        e.g. setup.cfg entry
        [translations]
        app_name = lizard-ui

        Throws an exception if not found.
        """
        try:
            app_name = self.config.get('translations', 'app_name')
        except (NoSectionError, NoOptionError, ValueError):
            raise Exception("no [translations] app_name entry in setup.cfg")
        else:
            return app_name


def _get_app_name():
    app = os.path.basename(os.getcwd())
    app_name = app.replace('-', '_')
    try:
        __import__(app_name)
        return app_name
    except ImportError:
        config = SetupConfig()
        try:
            print("Trying to import app name from setup.cfg: %s." % app_name)
            app_name = config.app_name()
        except Exception:
            print("Could not get app name from setup.cfg. Please add "
                  "[translations] app_name=<app_name> to your setup.cfg.")
        else:
            print("Trying to import app name from setup.cfg: %s." % app_name)
            try:
                __import__(app_name)
                return app_name
            except ImportError:
                print("Could not import app name from setup.cfg, got %s. "
                      "Please add [translations] app_name=<app_name> to your "
                      "setup.cfg." % app_name)
    sys.exit(1)  # get out if we get here


def _get_app_dir():
    app_name = _get_app_name()
    module = __import__(app_name)
    return os.path.dirname(os.path.abspath(module.__file__))


def _get_locale_dir():
    """Return the absolute path for the locale directory."""
    app_dir = _get_app_dir()
    locale_dir = os.path.join(app_dir, 'locale')
    return locale_dir


def _check_diff(cat_name, base_path):
    """
    Output the approximate number of changed/added strings in the en catalog.
    """
    po_path = '%(path)s/en/LC_MESSAGES/django%(ext)s.po' % {
        'path': base_path, 'ext': 'js' if cat_name.endswith('-js') else ''}
    p = Popen("git diff -U0 %s | egrep -v '^@@|^[-+]#|^..POT-Creation' | wc -l" % po_path,
              stdout=PIPE, stderr=PIPE, shell=True)
    output, errors = p.communicate()
    num_changes = int(output.strip()) - 4
    print("%d changed/added messages in '%s' catalog." % (num_changes,
                                                          cat_name))


def update_source_language_catalog(languages=None):
    """
    Update the en/LC_MESSAGES/django.po file with new/updated translatable
    strings.

    """
    cur_dir = os.getcwd()
    app_name = _get_app_name()
    app_dir = _get_app_dir()
    locale_dir = _get_locale_dir()

    os.chdir(app_dir)  # change to app_dir, needed for makemessages command
    print("Updating main en catalog")
    call_command('makemessages', locale='en')
    _check_diff(app_name, locale_dir)
    os.chdir(cur_dir)  # back to cur_dir


def upload_source_language_catalog(languages=None):
    """Upload source language catalog file. Consider doing this automatically
    via a GitHub web hook, that checks for locale/en/LC_MESSAGES/*.po file
    changes.

    """
    call('bin/%s push --source' % TX_CMD, shell=True)


def upload_translation_catalogs(languages=None):
    """Preferably not used, more for reference purposes."""
    if languages is None:
        call('bin/%s push --translations' % TX_CMD, shell=True)
    else:
        for lang in languages:
            call('bin/%s push -l %s' % (TX_CMD, lang), shell=True)


def fetch_language_files(languages=None):
    """
    Fetch translations from Transifex, wrap long lines, and generate mo files.

    """
    locale_dir = _get_locale_dir()
    app_name = _get_app_name()

    # Transifex pull
    if languages is None:
        call('bin/%s pull -a -f' % TX_CMD, shell=True)
        languages = sorted([d for d in os.listdir(locale_dir)
                            if not d.startswith('_')])
    else:
        for lang in languages:
            call('bin/%s pull -f -l %(lang)s' % (TX_CMD, lang), shell=True)

    # msgcat to wrap lines and msgfmt for compilation of .mo file
    for lang in languages:
        po_path = '%(path)s/%(lang)s/LC_MESSAGES/django%(ext)s.po' % {
            'path': locale_dir, 'lang': lang, 'ext': 'js' if app_name.endswith('-js') else ''}
        call('msgcat -o %s %s' % (po_path, po_path), shell=True)
        mo_path = '%s.mo' % po_path[:-3]
        call('msgfmt -o %s %s' % (mo_path, po_path), shell=True)


def main():
    RUNABLE_SCRIPTS = ('update_catalog', 'upload_catalog', 'fetch')

    parser = OptionParser(usage="usage: %prog [options] cmd")
    parser.add_option("-r", "--resources", action='append',
                      help="limit operation to the specified resources")
    parser.add_option("-l", "--languages", action='append',
                      help="limit operation to the specified languages")
    options, args = parser.parse_args()

    if not args:
        parser.print_usage()
        print("Available commands are: %s" % ", ".join(RUNABLE_SCRIPTS))
        sys.exit(1)

    cmd = args[0]
    if cmd in RUNABLE_SCRIPTS:
        if cmd == 'update_catalog':
            update_source_language_catalog()
        elif cmd == 'upload_catalog':
            upload_source_language_catalog()
        elif cmd == 'fetch':
            fetch_language_files()
    else:
        print("Available commands are: %s" % ", ".join(RUNABLE_SCRIPTS))


if __name__ == "__main__":
    main()
