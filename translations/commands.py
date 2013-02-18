#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from optparse import OptionParser
import os
from subprocess import call, Popen, PIPE
import sys

from django.core.management import call_command


logger = logging.getLogger(__name__)


TX_CMD = 'tx'  # needs buildout >= 2.0.1


def _get_app_name():
    app = os.path.basename(os.getcwd())
    app_name = app.replace('-', '_')
    return app_name


def _get_app_dir():
    app_name = _get_app_name()
    module = __import__(app_name)
    app_dir = os.path.dirname(os.path.abspath(module.__file__))
    return app_dir


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
