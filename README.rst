nens/translations
=================

Translations is a command-line tool for creating and updating translation source files on a
Transifex server and to fetch the translations from that server.

**Important**: make all strings translatable (english source) and only add and do translations via the Transifex server

Steps to create new resource in Transifex
-----------------------------------------
- generate a project and resource on https://translations.lizard.net
- use the same name structure like we use to name our projects on github: <project>/<resource>, e.g. lizardsystem/lizard-ui
- if not exists, create a .tx/config in the root of the translatable project, e.g.: lizard-ui/.tx/config (see example)
- create the desired translations in the corresponding resource, e.g. nl, zh, vi
- let the translators translate
- if translations are updated, run ``bin/transifex fetch`` command and commit

``<repo>/.tx/config`` example content:
::

    [main]
    host = https://translations.lizard.net
    type = PO

    [lizardsystem.lizard-ui]
    file_filter = lizard_ui/locale/<lang>/LC_MESSAGES/django.po
    source_file = lizard_ui/locale/en/LC_MESSAGES/django.po
    source_lang = en

Steps to add translations to project
------------------------------------
- add translations to project's setup.py (install_requires)
- use zc.buildout >= 2.0.1:
    - add zc.buildout >= 2.0.1 to project's setup.py (install_requires)
    - update buildout.cfg for 2.0.1:
        - add to [buildout] show-picked-versions = true
        - remove from [buildout] versions =
        - add to [versions] zc.buildout = 2.0.1
        - add to [console_scripts] dependent-scripts = true, and eggs =: add pyflakes and translations

Steps to update existing resource with updated source file (en)
---------------------------------------------------------------
- run ``bin/transifex update_catalog`` command
- commit updated source file to master and push to GitHub
- Transifex picks up the updated source file from GitHub and shows the new fields in the source and translation files

Required
--------
- GNU gettext for msgcat, msgfmt (sudo apt-get install gettext)
- <repo>/.tx/config
- ~/.transifexrc with transifex server credentials
- git

``~/.transifexrc`` example content:
::

    [https://translations.lizard.net]
    hostname = https://translations.lizard.net
    password = <password>
    token =
    username = <username>
