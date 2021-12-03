.. This file should contain the changes for the last release only, which
   will be included on the package's page on pypi. All older entries are
   kept in docs/HISTORY.rst

Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

6.0.0a2 (2021-12-03)
--------------------

Breaking changes:


- PLIP 3339: Replace ``z3c.autoinclude`` with ``plone.autoinclude``.
  Note: ``includeDependencies`` is no longer supported.
  [maurits, tschorr] (#3339)


New features:


- On Zope root, create Volto site by default.
  [maurits] (#3344)


Bug fixes:


- Move prefs_error_log* from skins to browser views
  [jmevissen] (#3241)
- The Plone site root is cataloged (#3314)
- Fix #3323DX-Site-Root: ZMI Nav-Tree is no longer expandable.
  [jensens] (#3323)
- Fixes #3337: 
  Remove dead code that wont work in Py 3 anyway if called (cmp).
  [jensens] (#3337)
- Remove DYNAMIC_CONTENT from translation files
  [erral] (#3342)
- Remove adapter for index location. [wesleybl] (#3347)
- Use document_view as default for site root.
  [agitator] (#3354)
- Add missing lxml dependency [MrTango] (#3356)
- Fixes #3352 - dependency indirection on plone.app.iterate [jensens] (#3357)
- In Portal: use security decorators
  [jensens] (#3366)
- Updated metadata version to 6002.  [maurits] (#6002)


6.0.0a1 (2021-10-22)
--------------------

Bug fixes:


- Release Plone 6.0.0a1.
  No changes since previous release.
  [maurits] (#3341)


6.0.0a1.dev1 (2021-10-16)
-------------------------

Bug fixes:


- Use HTML5 meta charset.
  [malthe] (#2025)
- add icon_expr to view/edit action for @@iconresolver
  [petschki] (#3327)
- Set the "Show excluded items" (``show_excluded_items``) to False per default.
  Setting it to ``True`` can introduce a performance problem.
  ``False`` should be the default, also from user expectation for the ``exclude_from_nav`` setting on content items.
  No upgrade step!
  Previous behavior is just kept, unless you override it manually.
  See: #3055, first comment.
  Use this registry snippet to set it false::

      <?xml version="1.0"?>
      <registry>
        <records prefix="plone" interface="Products.CMFPlone.interfaces.controlpanel.INavigationSchema">
          <value key="show_excluded_items">False</value>
        </records>
      </registry>

  Fixes: #3035
  [thet] (#3329)
- Remove typo in ajax_main_template
  [petschki] (#3333)
- Fix some template issues to have properly translated messages (#3334)
- Updated metadata version to 6001.
  [maurits] (#6001)


6.0.0a1.dev0 (2021-09-15)
-------------------------

Breaking changes:


- Removed our CMFQuickInstallerTool code completely.
  See `PLIP 1775 <https://github.com/plone/Products.CMFPlone/issues/1775>`_.
  [maurits] (#1775)
- Use Dexterity for the Plone Site root object.
  This is `PLIP 2454 <https://github.com/plone/Products.CMFPlone/issues/2454>`_.
  [jaroel, ale-rt] (#2454)
- Removed dependency on ``Products.TemporaryFolder``.
  Note: in your ``plone.recipe.zope2instance`` buildout part, you must set ``zodb-temporary-storage = off``,
  otherwise you get errors when starting Plone.
  See `issue 2957 <https://github.com/plone/Products.CMFPlone/issues/2957>`_.
  [maurits] (#2957)
- A part of "Drop Python 2 Support for Plone 6" #2812:
  Reflect dropping of Python 2 support in setup.py.
  Bump version to 6.0
  [jensens] (#3041)
- Removed ``folder_publish.cpy`` script.
  Replaced with folder_publish browser view in ``plone.app.content``.
  Removed deprecated transitionObjectsByPaths.
  [maurits] (#3057)
- Removed Products.CMFFormController dependency.
  [maurits] (#3057)
- Removed ``content_status_modify.cpy`` script and its validator ``validate_content_status_modify.vpy``.
  Replaced with ``content_status_modify`` browser view in ``plone.app.content``.
  [maurits] (#3057)
- Barceloneta LTS theming (#3061)
- Remove six at all places where used. [jensens] (#3183)
- Remove ``portal_utf8`` and it twin ``utf8_portal`` from ``utils`` and ``PloneTool`` since its never used nowhere. [jensens] (#3183)
- Remove `meta_type` index and metadata from catalog. 
  Both were unused in Plone core and rarely used in addons.
  [jensens] (#3208)
- Plone 6 with markup update for Bootstrap.
  Extensive overhaul of Plone ui elements based on Bootstrap components.
  Introduction of icon resolver with use of icon_epr definitions.
  [1letter, agitator, ale-rt, balavec, ericof, erral, frapell, fredvd, fulv, gomez, jensens, krissik,
  mauritsvanrees,  mrtango, nilshofer, petschki, santonelli, thet, thomasmassmann, tkimngyuen,
  tschorr] (#3249)


New features:


- Custom date format strings from registry can be in the ``${}`` format as in the locales files. 
  If theres a day or month name used, this will be translated. 
  For bbb the classic strftime ``%`` strings are still behaving like before.
  [jensens] (#3084)
- Add icon resolver to return url or tag for given icon.
  [santonelli] (#3192)
- Include a controlpanel to inspect and rebuild relations.
  [pbauer] (#3231)
- Add PLONE60MARKER (and PLONE52MARKER) Python marker
  [sneridagh] (#3257)
- Protect @@historyview with Modify portal content permission. Fixes #3297
  [pbauer] (#3297)


Bug fixes:


- Add ``plone.app.caching`` to the list of add-ons that is upgraded when upgrading Plone.
  [maurits] (#82)
- Change control panel item sorting and sort them by title
  [erral] (#721)
- No longer doubly undo a response Content-Type change when combining bundles.
  [maurits] (#1924)
- Removed dependency on Products.Sessions.
  It is still pulled in by Products.PluggableAuthService though.
  See also `CMFPlacefulWorkflow issue 35 <https://github.com/plone/Products.CMFPlacefulWorkflow/issues/35>`_.
  [maurits] (#2957)
- Fix issue with @@search view when filtering by creation date
  [frapell] (#3007)
- Merge Hotfix20200121: isURLInPortal could be tricked into accepting malicious links. (#3021)
- Merge Hotfix20200121 Check of the strength of password could be skipped. (#3021)
- Improve tests for the workflow tool method listWFStatesByTitle (#3032)
- A default WSGI configuration requires Paste which is only installed with the Zope[wsgi] extra..
  [tschorr] (#3039)
- Fixed deprecation warning for zope.site.hooks.
  [maurits] (#3130)
- Fixed use of own ``utils.isDefaultPage``, which should be ``defaultpage.check_default_page_via_view``.
  [maurits] (#3130)
- Fixed invalid escape sequences in regular expressions.
  [maurits] (#3130)
- PloneBatch: define ``__bool__`` as copy of ``__nonzero__``.
  Python 3 calls ``__bool__`` when doing ``bool(batch)``.
  [maurits] (#3175)
- No longer consider calling ``len(batch)`` as deprecated.
  The deprecation warning is unvoidable with current ``Products.PageTemplates`` code.
  Fixes `issue 3176 <https://github.com/plone/Products.CMFPlone/issues/3176>`_.
  maurits (#3176)
- Fix tests with Products.MailHost 4.10.
  [maurits] (#3178)
- Applied: `find . -name "*.py" |grep -v skins|xargs pyupgrade --py36-plus --py3-only`.
  This auto-rewrites Python 2.7 specific syntax and code to Python 3.6+.
  [jensens] (#3185)
- Robot tests: Do not use jQuery.size() but use ``.length`` instead.
  ``.size()`` is deprecated since 1.8.
  [thet] (#3195)
- Remove traces of Archetypes
  [pbauer] (#3214)
- Fix problem to remove username and password from email settings if there was already one set. 
  [jensens] (#3224)
- Fix migration when we have broken objects in the app root (e.g. the temp_folder) (#3245)
- Fixed tests in combination with Products.PluggableAuthService 2.6.0.
  [maurits] (#3251)
- Fix closing curly brace in search.pt template.
  [balavec] (#3252)
- Add the remote code execution fix from the `Products.PloneHotfix20210518 expressions patch <https://plone.org/security/hotfix/20210518/remote-code-execution-via-traversal-in-expressions>`_.
  We need this because Zope 4.6.2 is too strict for us.
  [maurits] (#3274)
- Removed the docstring from various methods to avoid making them available via a url.
  From the `Products.PloneHotfix20210518 reflected XSS fix <https://plone.org/security/hotfix/20210518/reflected-xss-in-various-spots>`_.
  [maurits] (#3274)
- Remove unused imports. [jensens] (#3299)
- Fix TypeError when adding a portlet. [daggelpop] (#3303)
- The portal catalog will not try to index itself anymore [ale-rt] (#3312)
