.. This file should contain the changes for the last release only, which
   will be included on the package's page on pypi. All older entries are
   kept in HISTORY.txt

Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

5.2rc1 (2019-03-04)
-------------------

New features:


- Views for title and description. [iham] (#2740)
- Display wsgi-state plus name and version of the server in the controlpanel
  [pbauer] (#2770)
- Enable dropdown-navigation for new sites by default. [pbauer] (#2772)


Bug fixes:


- Resolve circular dependency between `Products.CMFPlone` and `plone.i18n` by
  moving `ILanguageSchema` there. [sallner] (#2049)
- Use correct permission for mail controlpanel form so that Site Administrators
  can also edit. [fredvd] (#2688)
- - make linkintegrity robot test more reliable [MrTango] (#2752)
- Check only once if Products.ATContentTypes is available. [gforcada] (#2765)
- Fix redirection to `came_from` when url matches LOGIN_TEMPLATE_ID partly
  [petschki] (#2771)


5.2b1 (2019-02-13)
------------------

Breaking changes:


- - Factor out all static resources and the ``plone-compile-resources`` script
  into plone.staticresources. [thet] (#2542)


New features:


- PLIP 1486: Merge Products.RedirectionTool into core. Allow users to manage
  redirects on their site and aliases to content. See
  https://github.com/plone/Products.CMFPlone/issues/1486 [staeff, maurits]
  (#1486)
- - Added multilevel dropdown navigation [agitator] (#2516)
- No longer mark special links by default. [pbauer] (#2736)


Bug fixes:


- Switched allowedRolesAndUsers indexer from 'View' to the correct permission
  'Access contents information' for displaying metadata. 'View' permission
  should be used on the item itself. The change should not matter for default
  Plone workflows, since they always use those permissions together. [agitator]
  (#260)
- deprecate catalog_get_all(catalog) in favor of catalog.getAllBrains()
  [pbauer] (#2258)
- Restore the possibility to sort catalog query results with multiple indexes
  (#2464)
- Review list portlet showed nothing to review with plone.app.multilingual, As
  WorkflowTool bypassed languages only for p.a.m<2.x or linguaplone. fixed and
  now compatible to both lang-bypassing methods. [iham] (#2595)
- Fixed fallback to default view when selected layout does not exist for
  Folder. [gbastien] (#2645)
- The patched init method for the class zope.sendmail.mailer.SMTPMailer has
  been updated, fixing a bug that was preventing to send emails. [ale-rt,
  nazrulworld] (#2665)
- a11y: Added role attribute for portalMessage [nzambello] (#2675)
- Fix several warnings shown when running tests on Python 3+. [gforcada]
  (#2683)
- fixed Python 3 related str decoding issue in breadcrumbs (#2694)
- Fixed unstable robot test Scenario: A page is opened to edit in TinyMCE.
  [maurits] (#2707)


5.2a2 (2018-12-30)
------------------

New features:


- New robot tests for querystring in Collection type. Now almost all
  querystring types are robot tested. [llisa123] (#2489)
- Add ``load_async`` and ``load_defer`` attributes to resource registries
  bundle settings. When set, ``<script>`` tags are rendered with
  ``async="async"`` resp. ``defer="defer"`` attributes. You also need to empty
  the ``merge_with`` property of your bundle, because production bundles
  (``default.js`` and ``logged-in.js``) are never loaded with async or defer.
  The default.js includes jQuery and requirejs and those are needed at many
  places and therefore cannot be loaded asynchronously. Refs: #2649, #2657.
  [thet] (#2649)


Bug fixes:


- Delete ``fa_ir.js``. Keep ```fa_IR.js``. [maurits] (#2620)
- Forward port TinyMCE fixes from 5.1 [vangheem] (#2630)
- Fix robot test test_edit_user_schema: Fieldname was set duplicate (first by
  JS, then by robot). [jensens] (#2669)

5.2a1 (2018-11-08)
------------------

Breaking changes:

- Removed generateUniqueId.py skins script (after it was added to Products.Archetypes).
  This script is no longer available outside Archetypes world.
  #1801
  [jensens]

- Remove all dependencies on plone.app.controlpanel.
  Third party code need either to depend on plone.app.controlpanel 4.0,
  which is a backward compatibility package only, or also update to not depend on it anymore.
  [jensens]

- Removed check_id.py skin script.  Replaced with utils.check_id function.
  #1801 and #2582.
  [maurits]

- Removed my_worklist.py skin script. #1801
  [reinhardt]

- Removed getObjectsFromPathList.py skin script. #1801
  [reinhardt]

- Removed isExpired.py skin script. #1801
  [reinhardt]

- Removed redirectToReferrer.py skin script. #1801
  [tlotze]

- Removed enableHTTPCompression.py skin script. #1801
  [tlotze]

- Removed setAuthCookie.py skin script. #1801
  [tlotze]

- Stop configuring 'View History' permission which was removed from Zope.
  [davisagli]

- Removed legacy resource registries portal_css and portal_javascripts;
  no conditional handling.
  [ksuess]

New features:

- Factored out human_readable_size method for replacing getObjSize.py;
  removed getObjSize.py. #1801
  [reinhardt]

- Update TinyMCE to 4.7.13
  [erral]

- New browser view based login code - merged from plone.login (credits to esteele, pbauer, agitator, jensens, et al).
  `portal_skins/plone_login` is now gone, see PLIP #2092.
  Also, password reset view moved to login subfolder to keep things together.
  Some testbrowser based tests needed changes because of z3c.form based login form .
  The Plone specific, rarely used cross site __ac cookie SSO feature/hack was removed.
  In case somebody needs this, please make it an addon package.
  Better use a field proven, more secure way, like OAuth2, Shibboleth or someting similar.
  [jensens, et al]

- Upgrade grunt + plugins to same versions as in
  mockup https://github.com/plone/mockup/pull/870
  [sunew]

- Upgrade less in bower.json to the same version as already used
  in the generated package.json in compile_resources.py.
  [sunew]

- Add utility-method safe_nativestring.
  [pbauer]

- Rename safe_unicode to safe_text and safe_encode to safe_bytes. Keep old aliases.
  [pbauer]
- Add a ``bin/instance verifydb`` command which can be used to check
  that all records in the database can be successfully loaded.
  This is intended to help with verifying a database conversion
  from Python 2 to Python 3.
  [davisagli]

Bug fixes:

- Modernize robot keywords that use "Get Element Attribute"
  [ale-rt]

- remove plone.app.folder dependency
  [petschki]

- move GopipIndex Class to plone.folder
  [petschki]

- Fixed getObjSize indexer for Python 3. #2526
  [reinhardt]
- Fix toolbar menu on mobile #2333.
- make groups_modify_roles test more robust.
  [tschorr]

-- Fix wrong CSS property to allow correct word-break.
  [tmassman]

 Fix toolbar menu on mobile #2333.
  [tmassman]

- Removed the ``raiseUnauthorized`` skin script.
  If you use this, please do permission checking in your own Python code instead (likely in a browser view).
  Refs `issue 1801 <https://github.com/plone/Products.CMFPlone/issues/1801>`_.
  [maurits]

- Remove the devdependencies from bower.json - they are just used for running tests in mockup, not here.
  [sunew]

- Adapt tests to `Products.GenericSetup >= 2.0` thus requiring at least that
  version.
  [icemac]

- Some tools from CMFCore are now utilities
  [pbauer]

- Fix failing thememapper robot test after rebuild of thememapper bundle in p.a.theming PR 148
  [sunew]

- Remove five.pt for Zope 4
  [jensens]

- Changes for Zope 4 compatibility in maintenance controlpanel.
  [thet]

- Render exceptions using an exception view instead of standard_error_message.
  [davisagli]

- Remove old PlacelessTranslationService.
  [jensens, ksuess]

- Fix controlpanel quickinstaller view:
  A not yet installed product must not return any upgrade info.
  [jensens]

- Fix to make plone/plone.session#11 work:
  Make test for installation of  plone.session more explicit.
  [jensens]

- Advanced Catalog Clear And Rebuild feature showed wrong processing time due to new queue processing.
  This was fixed bei calling ``processQueue()`` after indexing.
  [jensens]

- Some nested `section id="edit-bar"` tag in folder_contents page #2322
  [terapyon]

- Remove ``plone-generate-gruntfile`` (it is all available through ``plone-compile-resources``).
  [jensens]

- Migrate from ``slimit`` to ``calmjs.parse`` for the JavaScript cooker #2616
  [metatoaster]


New Features:

- Update to latest mockup
  [frapell]

- Provide an utility ``dump_json_to_text`` that works both on Python 2.7 an Python 3.
  [ale-rt]

- Prepare for Python 2 / 3 compatibility.
  [pbauer]

- Fix imports to work with Python 3.
  [pbauer]

- Mockup update.
  [thet]

- add link to Plone.org VPAT accessibility statement
  [tkimnguyen]

Bug Fixes:

- Remove last legacy Javascript ``highlight-searchterms.js``.
  Removes also the skins folder ``plone_ecmascript``.
  It was broken for all (Google, other search engines, own live search);
  JS worked only when coming from Plone detailed search.
  [jensens]

- Fix an undefined variable in a test helper function
  [ale-rt]

- Let the ``combine-bundles`` import step also work when the ``IBundleRegistry`` keyword is not in ``registry.xml``, but in a ``registry`` directory.
  `Issue 2520 <https://github.com/plone/Products.CMFPlone/issues/2502>`_.
  [maurits]

- Get rid of obsolete ``X-UA-Compatible`` header.
  [hvelarde]

- Fix registration of ``robots.txt`` browser view to avoid ``AttributeError`` on Zope's root (fixes `#2052 <https://github.com/plone/Products.CMFPlone/issues/2052>`_).
  [hvelarde]

- Get rid of obsolete ``X-UA-Compatible`` header.
  [hvelarde]

- Add test for issue #2469.
  [jensens]

- Fixed tests when IRichText behavior is used.
  IRichText -> IRichTextBehavior
  This is a follow up to `issue 476 <https://github.com/plone/plone.app.contenttypes/issues/476>`_.
  [iham]

- Remove unused mail_password.py from skins/plone_scripts
  [agitator]

- Hide ``plone.app.querystring`` from add-ons control panel.
  Fixes `issue 2426 <https://github.com/plone/Products.CMFPlone/issues/2426>`_.
  [maurits]

- Fix tests after changes in disallowed object ids in Zope.
  [pbauer]

- Do not include too new upgrades when upgrading Plone Site.
  Otherwise the Plone Site ends up at a newer version that the filesystem code supports,
  giving an error when upgrading, and resulting in possibly missed upgrades later.
  Fixes `issue 2377 <https://github.com/plone/Products.CMFPlone/issues/2377>`_.
  [maurits]

- After site creation, do not render the add-site template: we redirect anyway.
  [maurits]

- Unflakied a unit test.
  [Rotonen]

- Do not show TinyMCE menu items with no subitems, Fixes #2245.
  [mrsaicharan1]

- Fix Exception-View when main_template can't be rendered. Fixes #2325.
  [pbauer]

- Render exceptions as text, not html to fix format of infos after traceback.
  Display as <pre> for basic and normal error templates.
  [pbauer]

- Removed extra methods and tests for CMFQuickInstallerTool.
  Moved those to the Products.CMFQuickInstallerTool package.
  [maurits]

- Added tests for add-ons control panel.
  Add a link to the Site Setup.
  Let ``get_product_version`` work when you call it with ``CMFPlacefulWorkflow`` too.
  [maurits]

- Fix bad domain for translating password reset mails.
  [allusa]

- Ignore invalid ``sort_on`` parameters in catalog ``searchResults``.
  Otherwise you get a ``CatalogError``.
  I get crazy sort_ons like '194' or 'null'.
  [maurits]

- Register the ``ExceptionView`` for the unspecific ``zope.interface.Interface`` for easier overloading.
  Fixes a problem, where plone.rest couldn't overload the ExceptionView with an adapter bound to ``plone.rest.interfaces.IAPIRequest``.
  [thet]

- Fixed linkintegrity robot tests.  [maurits]

- Fixed flaky actions controlpanel tests by waiting longer.  [maurits]

- Require AccessControl 4.0b1 so ``guarded_getitem`` is used.
  Part of PloneHotfix20171128.  [maurits]

- Improved isURLInPortal according to PloneHotfix20171128.
  Accept only http/https, and doubly check escaped urls.  [maurits]

- Fix exception view when called on Zope-root. Fixes #2203.
  [pbauer]

- added CSS hyphenation support for toolbar for avoiding ugly text wrapping
  Fixes `issue 723 <https://github.com/plone/Products.CMFPlone/issues/723>`_.
  [ajung]

- Increase compatibility with Python3.
  [ale-rt]

- Show example for expression in actions control panel.
  [maurits]

- Fix test where you cannot instanciate a PythonScript with the id script.
  [pbauer]

- Set the status of an exception view according to the exception type.
  Fixes `issue 2187 <https://github.com/plone/Products.CMFPlone/issues/2187>`_.
  [maurits]

- Use absolute imports for Python3 compatibility
  [ale-rt]

- Fallback for missing date in DefaultDublinCoreImpl no longer relies on
  bobobase_modification_time.
  [pbauer]

- Display real version of Zope, not of the empty meta-package Zope2.
  [pbauer]

- Add zcml-condition plone-52 for conditional configuration.
  [pbauer]

- Use getSite in set_own_login_name to get the portals acl_users.
  [pbauer]

- Fix test issue with rarely used multi-site SSO feature.
  ``came_from`` on ``@register`` link would point to wrong site.
  Completly removed ``came_from`` on ``@@register`` link.
  It does not make much sense anyway and we test nowhere if there is a came_from on that link.
  [jensens]

- Remove depricated ``type`` attribute from ``script`` and ``link`` tags.
  [newbazz]

- Render tinymce attributes correctly in Python3.
  [sallner]

- Remove unresolved dependencies of plone-final to cssregistry and jsregistry.
  [pbauer]
