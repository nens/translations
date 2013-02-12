translations
============

Translations is a project to create and update translation source file on a
Transifex server and to fetch translation files.

General workflow idea (in progress)
-----------------------------------
Do it the django way:
  see django/scripts/manage_translations.py

Steps to create new resource in Transifex:
- if not exists, generate a project and resource on https://translations.lizard.net
- for that, use same name structure like we use to name our projects on github:
	<project>/<resource>, e.g. lizardsystem/lizard-ui
- if not exists, create a .tx/config in the root of the translatable project, e.g.:
    lizard-ui/.tx.config example:
    ---
    [main]
    host = https://translations.lizard.net
    type = PO

    [lizardsystem.lizard-ui]
    file_filter = lizard_ui/locale/<lang>/LC_MESSAGES/django.po
    source_file = lizard_ui/locale/en/LC_MESSAGES/django.po
    source_lang = en
	---
    (consider creating a command for creating this interactively)
- create the desired translations in the corresponding resource, e.g. nl, zh, vi
- let the translators translate
- if translations are updated, run `fetch` command and commit

Steps to update existing resource with updated source file (en):
- run `update_catalog` command
- run `upload_catalog` command
- commit updated source file to master

Required:
	- GNU gettext for msgcat, msgfmt (sudo apt-get install gettext), consider
  creating a check to be sure that these are installed
	- <repo>/.tx/config
	- ~/.transifexrc
	- git for _check_diff function
