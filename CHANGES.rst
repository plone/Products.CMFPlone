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

6.0.0rc1 (2022-11-18)
---------------------

Bug fixes:


- Don't create news, events, and users folders for Volto sites. [davisagli] (#3628)
- Fix password used in a test. [davisagli] (#3653)
- Bootstrap fix for numbering `.list-group-numbered`.
  See suggestions here https://github.com/twbs/bootstrap/issues/37345
  [petschki] (#3661)
- Fix 'KeyError: file' in browser tests on Python 3.11.
  [maurits] (#3663)
- Updated metadata version to 6009.  [maurits] (#6009)


6.0.0b3 (2022-10-04)
--------------------

Bug fixes:


- Deprecate the portal_properties tool, remove obsolete code (#125)
- Require Python 3.8 or higher.  [maurits] (#3635)
- Actually load theme-specified styles CSS in TinyMCE. [Rudd-O] (#3638)
- Minor visual fixes in admin UI [jensens] (#3640)
- Fix aliased helpers
  [ale-rt] (#3641)
- Fix tests to work with longer minimum password length. [davisagli] (#3646)
- Improve tinymce table settings [MrTango] (#3650)
- Make add classic Plone site button better visible [MrTango] (#3651)
- Updated metadata version to 6008.  [maurits] (#6008)


6.0.0b2 (2022-09-10)
--------------------

Breaking changes:


- Officially drop Python 3.7 support and add 3.10 support.
  Currently everything still work in 3.7, all tests pass, but beta 2 is the last release where this is the case.
  See discussion in `this issue <https://github.com/plone/Products.CMFPlone/issues/3635>`_ and especially `this community poll <https://community.plone.org/t/plone-6-0-drop-support-for-python-3-7-and-3-8/15549>`_.
  [maurits] (#3635)


Bug fixes:


- Moved CSFR patches addressing CMFPlone itself to decorators.
  [jensens] (3614-2)
- Fixed an issue that prevented the user to select the preferred timezone (#1290)
- Fixed adding control panel action via ZMI.
  [maurits] (#1959)
- Changed 'Powered by' text
  [rohnsha0] (#3382)
- Fix active tab in ``@@test-rendering-icons``.
  [petschki] (#3475)
- Do not create title tag for svg icons when tag_alt is not given.
  [agitator] (#3536)
- Fixed all known instances of plone.com in plone/Products.CMFPlone
  [rohnsha0] (#3568)
- Allow access to the macros of the main_template, also from skin templates.
  [maurits] (#3581)
- Robot tests: be more specific when clicking some elements.
  [maurits] (#3582)
- Set portal title in registry when creating a new Plone site
  [erral] (#3584)
- Change test to make sure e-mail is sent in utf-8
  [erral] (#3587)
- Fixed 'Site Setup' link appearing on various parts of Control Panel
  [rohnsha0] (#3599)
- Fixed Inconsistent font issues in Control Panel
  [rohnsha0] (#3600)
- Fix visual issue with long action name in @@actions-controlpanel.
  [petschki] (#3601)
- Fixed an error where Main Template (line: 42) referenced plone.com istead of plone.org
  [rohnsha0] (#3605)
- In traversal.py remove a Zope 4 BBB code, add a comment about bundle traverser and apply black.isort on the file.
  [jensens] (#3609)
- Supress warning of intentional deprecated import for BBB.
  [jensens] (#3610)
- Use plone.base and reduce deprecation warnings.
  In utils remove functions already moved to plone.base and add deferred import with message.
  Deprecate correct, where prior only comments or old logging.
  Some black/isort where touched.
  [jensens] (#3614)
- Move utils.getQuality and utils.getAllowedSizes to plone.namedfile.utils.
  This helps untangling circular dependencies.
  [jensens] (#3615)
- Do not use deprecated calls in actions expressions.
  ActionsTool and PloneBasetool got an code style overhaul.
  [jensens] (#3616)
- Updated metadata version to 6007.
  [maurits] (#6007)


6.0.0b1 (2022-07-23)
--------------------

Breaking changes:


- Removed our expressions patch.
  This was a patch to avoid some too strict checks by Zope / Products.PageTemplates.
  But in Plone 6 it should be fine to be stricter.
  The ``STRICT_TRAVERSE_CHECK`` environment variable is no longer read.
  [maurits] (#3567)


New features:


- Initially open accordions in resource registry. Hide via JS when no errors occur.
  [petschki] (#3560)
- Resource bundle dependency on multiple comma separated names.
  [petschki] (#3570)


Bug fixes:


- Reduce dependencies in setup.py here, when already fulfilled in the packages where in use.
  [jensens] (#3572)
- Fix more plone.base related deprecation warnings.
  [jensens] (#3573)
- Fix adding/renaming resources TTW.
  [petschki] (#3574)
- More i18n fixes
  [erral] (#3575)
- Updated metadata version to 6006.
  [maurits] (#6006)


6.0.0a6 (2022-06-27)
--------------------

Bug fixes:


- Remove the use of f-strings for translations
  [erral] (#3564)
- Fix several i18n bugs
  [erral] (#3565)
- Fix tests for `image_scale` download url update.
  [petschki] (#3566)


6.0.0a5 (2022-06-24)
--------------------

Breaking changes:


- Remove Archtypes specific ``isIDAutoGenerated`` helper.
  This was dead code not used anywhere in Plone 6.
  [jensens] (#3487)
- ``PloneFolder`` was once used with early Archetypes.
  This code is dead now and got removed.
  [jensens] (#3492)
- ``DublinCore.py`` was once used with Archetypes.
  This code is dead now and got removed.
  [jensens] (#3493)
- Move discussion Key to ``plone.app.discussion``.
  [jensens] (#3520)


New features:


- Added customisable batch_size for redirects controlpanel
  [iulianpetchesi] (#1178)
- Add option to use TinyMCE in inline-mode.
  [pbauer] (#3465)
- Add image srcset's configuration to TinyMCE pattern settings [MrTango] (#3477)
- Add support for images in default search page.
  [agitator] (#3495)
- Enable auto include of styles to the TinyMCE formats menu. The file has to be named ``tinymce-formats.css`` and known by TinyMCE.
  [agitator] (#3510)
- Add ``image_scales`` to catalog metadata.
  [cekk, maurits] (#3521)
- Sort addons by title
  [erral] (#3523)
- Show more information of broken relations
  [pbauer] (#3527)
- Show link to the Volto-migration (``@@migrate_to_volto``) in the view ``@@plone-upgrade`` when the option is available.
  [pbauer] (#3528)
- SVG image as default Plone logo.
  [petschki] (#3558)


Bug fixes:


- Make compatible with robotframework 3-5.
  [maurits] (#5)
- Explicitly include zcml of more packages.
  Reorder the zcml loading.
  Require ``plone.resource``.
  [maurits] (#3188)
- Remove date range search fix, which was done in Products.ZCatalog.
  [wesleybl] (#3432)
- fix `@@iconresolver` to resolve names with "/" correctly (eg. "contenttype/document")
  [petschki] (#3500)
- Bugfix: Resource viewlet cache took not enough factors into account (like base url).
  [jnsens] (#3503)
- Moved ``recently_modified`` and ``recently_published`` skin templates to browser views.
  [maurits] (#3515)
- Fix for quoted search terms
  [petschki] (#3517)
- Fix robot tests for updated toolbar
  [petschki] (#3522)
- Fix rendering viewlet.resourceregistries.js when there are missing resources.
  [petschki] (#3533)
- Fix tests for updated module federation bundles.
  [thet] (#3539)
- Remove modal from login and join action.
  [agitator] (#3555)
- Fix reporting of exceptions in Products.CMFPlone.factory.addPloneSite.
  [davisagli] (#3561)
- Updated metadata version to 6005.
  [maurits] (#6005)


6.0.0a4 (2022-04-08)
--------------------

Breaking changes:


- PLIP 3211:

  - Remove RequireJS.
  - Remove default resource jQuery. It is added to the global namespace via the bundle.
  - Remove support for conditional comments in script and style tags.
    It's not supported since IE10.
    See: https://en.wikipedia.org/wiki/Conditional_comment

  [MrTango, thet] (#3247)
- Remove dependency on mockup. Mockup is now a npm package only and as such a dependency of plone.staticresources.
  [thet] (#3247)
- New resource registry to simplify CSS/JS registration.

  - Completely (almost) rewritten ResourceRegistry based on the "webresource" project.
  - removed >1600LOC.
  - Sane dependency resolution using "webresource".
  - Only "bundles" are registered - support of "resources" and "bundle resources" is removed.
  - Some of the old bundle registry properties are deprecated and unused.
  - Removed TTW compilation of bundles via r.js and less.js.
  - Property ``merge_with`` is no longer needed in HTTP/2 times and merging here unsupported.
  - Unique key for delivery is based on hash of bundle file, ``last_compilation`` property is deprecated.
  - A new traverser ensures uniqueness.
  - Other related bundle properties are also deprecated.
  - Comes with new, server side generated control panel.

  [jensens] (#3325)
- Remove ``deprecated.zcml`` and ``meta-bbb.zcml``.
  [jensens, pbauer] (#3485)


New features:


- PLIP #3279: Implement modern images scales. Add huge (1600px), great (1200px), larger (1000px), teaser (600px). Amend preview and mini (remove height constraint).
  [tisto] (#3279)
- Add TinyMCE template plugin to the plugins vocabulary [MrTango] (#3351)
- Implement `PLIP 3395 <https://github.com/plone/Products.CMFPlone/issue/3395>`_.
  Moves all interfaces, whole defaultpage, i18nl10, batch, permissions and parts of utils to ``plone.base``.
  For all imports are in place with deprecation warnings.
  Along with this a bunch of long deprecated functions, imports and similar in above packages were removed.
  [jensens] (#3395)
- Add TinyMCE alignment classes, to avoid style usage [MrTango] (#3440)
- Compatibility with z3c.form >= 4
  [petschki] (#3459)
- Added support for images in liveSearch results.
  [agitator] (#3489)


Bug fixes:


- Fixed evaluating expressions on resources, and especially loading ``plone.session`` resources.
  Fixes `plone.session issue 23 <https://github.com/plone/plone.session/issues/23>`_.
  [maurits] (#23)
- MigrationTool: use more standard ``listUpgrades`` code from GenericSetup 2.2.0.
  I ported our special logic there.
  [maurits] (#220)
- Handle /favicon.ico accesses on Plone sites. (#282)
- Fixed tests when run with ``zope.component`` 5+.
  [maurits] (#500)
- Remove Configlets, Change Member Password and Member Prefs not needed in Overview Controlpanel
  both Views available via User Control Panel

  the deleton of "Change Member Password" Configlet remove also the issue #3031
  [1letter] (#3031)
- Removed no longer used ``password_form.pt`` and ``plone_change_password.py``.
  No longer register now empty skin layers ``plone_prefs`` and ``plone_form_scripts``.
  [maurits] (#3240)
- Fix TinyMCE configuration JSON serialization and cast entity_encoding to a list. (#3247)
- Make author template barceloneta/bs5 ready. Add some CSS classes to Markup.
  [1letter] (#3290)
- Use behavior-names instead of python-paths in types-controlpanel
  [pbauer] (#3294)
- Fix broken link in the RelationsInspectControlpanel
  prepend absolute portal url to links
  add RelationsControlPanelFunctionalTest
  [1letter] (#3322)
- Fix missing closing BODY tag in insufficient_privileges.pt
  [1letter] (#3374)
- Reorganize viewlets after removing the plone.header viewlet in plone.app.layout
  [erral] (#3416)
- Fix ``login-help`` validation
  [petschki] (#3422)
- Fix info message (char left over) in quickinstaller template
  [laulaz] (#3430)
- Fix overview-controlpanel view for Gunicorn WSGI HTTP Server.
  [bsuttor] (#3442)
- Fix detection of initial login time [MrTango] (#3447)
- Updated the list of core profiles that are upgraded during a Plone upgrade.
  Added ``Products.PlonePAS`` and ``plone.session``, and the optional ``plone.restapi`` and ``plone.volto``.
  [maurits] (#3453)
- Remove obsolete css files previously used in tinymce.
  [pbauer] (#3463)
- Add missing i18n:translate tags
  [erral] (#3467)
- Remove obsolte combine_bundles and related code.
  [pbauer] (#3468)
- Enhanced folder_contents robot tests
  [petschki] (#3478)
- Updated metadata version to 6004.
  [maurits] (#6004)


6.0.0a3 (2022-01-28)
--------------------

New features:


- add a new entry in site-controlpanel to change the favicon and its MIME-type
  The favicon can be a .ico/png or SVG-file
  [talarias] (plip-barceloneta_lts_favicon)
- The @@plone view exposes the human_readable_size helper
  [ale-rt] (#3146)
- Allow ``from warnings import warn`` and ``warn("message", DeprecationWarning)`` TTW, like in Python Scripts.
  [jensens] (#3376)
- Customize breadcrumbs hook ``customize_entry`` for subclasses (like already in global navigation).
  [jensens] (#3377)


Bug fixes:


- Cleanup Error Log Form after Review
  [jmevissen] (#3241)
- Removed management_page_charset support from usergroup-groupdetails page.
  This is related to deprecated unicode property types, like ustring.
  Part of `issue 3305 <https://github.com/plone/Products.CMFPlone/issues/3305>`_.
  [maurits] (#3305)
- Update Controlpanel Error Log Form Layout
  Rename ControlPanel Error Log Form View prefs_error_log_form -> error-log-form
  [jmevissen] (#3393)
- Use label_site_administration instead of label_site_admin in error and mail_password_form templates (#3397)
- Updated metadata version to 6003.  [maurits] (#6003)


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
