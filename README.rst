nens/translations
=================

Translations is a command-line tool for creating and updating translation
source files on a Transifex server and to fetch the translations from that
server.

**Important**: make all strings translatable (english source) and only add and
do translations via the Transifex server.

Steps to create new resource in Transifex
-----------------------------------------

- Make sure you have the English translation files locally available.

  - TODO: add documentation

  - e.g. ``mkdir lizard_wms/locale``

  - ``bin/django i18n -l en``

  - ``lizard_wms/locale/en/LC_MESSAGES``

- Generate a project and resource on https://translations.lizard.net.

- Use the same name structure like we use to name our projects on github:
  ``<project>/<resource>``, e.g. lizardsystem/lizard-ui.

- If not exists, create a ``.tx/config`` in the root of the translatable
  project, e.g.: ``lizard-ui/.tx/config`` (see example).

- Create the desired translations in the corresponding resource, e.g. nl, zh,
  vi.

- Let the translators translate.

- If translations are updated, run ``bin/transifex fetch`` command, check if
  everything is fine, commit and push to GitHub.

``<repo>/.tx/config`` example content::

    [main]
    host = https://translations.lizard.net
    type = PO

    [lizardsystem.lizard-ui]
    file_filter = lizard_ui/locale/<lang>/LC_MESSAGES/django.po
    source_file = lizard_ui/locale/en/LC_MESSAGES/django.po
    source_lang = en


Steps to add translations to project
------------------------------------

- Add ``translations`` to your project's ``setup.py`` (``install_requires``).

- Use ``zc.buildout`` >= ``2.0.1``:

  - Add ``zc.buildout >= 2.0.1`` to your project's ``setup.py``
      (``install_requires``).

  - Update ``buildout.cfg`` for ``2.0.1``:

    - Add to ``[buildout]``: ``show-picked-versions = true``

    - Remove from ``[buildout]``: ``versions =``

    - Add to ``[versions]``: ``zc.buildout = 2.0.1``

    - Add to ``[console_scripts]``: ``dependent-scripts = true``, and
      ``eggs =``: add ``pyflakes`` and ``translations``.

    - TODO: add bootstrap.py

      ``wget http://downloads.buildout.org/2/bootstrap.py``

- Put translations entry with app_name in ``setup.cfg``, if repo name can not
  be resolved to app name (repo name should be same as app name
  (e.g. controlnext/controlnext) or by replacing hyphen with underscore,
  e.g. lizard-ui -> lizard_ui).

``setup.cfg`` example translations section::

    [translations]
    app_name = flooding_lib


Steps to update existing resource with updated source file (en)
---------------------------------------------------------------

- Run ``bin/transifex update_catalog`` command.

- Commit updated source file to master and push to GitHub.

- Transifex picks up the updated source file from GitHub and shows the new
  fields in the source and translation files.

- TODO: for that to work, add a source file url by clicking on "edit this
  resource" in the transifex interface for your project. The url should be the
  raw github url of the English ``.po`` file.


Required
--------

- GNU gettext for msgcat, msgfmt (``sudo apt-get install gettext``).

- ``<repo>/.tx/config``

- ``~/.transifexrc`` with transifex server credentials

- git

``~/.transifexrc`` example content::

    [https://translations.lizard.net]
    hostname = https://translations.lizard.net
    password = <password>
    token =
    username = <username>
