.. This file should contain the changes for the last release only, which
   will be included on the package's page on pypi. All older entries are
   kept in HISTORY.txt

Changelog
=========

5.1.4.rc2 (2018-10-03)
----------------------

Bug fixes:

- added CSS hyphenation support for toolbar for avoiding ugly text wrapping
  Fixes `issue 723 <https://github.com/plone/Products.CMFPlone/issues/723>`_
  and `issue 2315` <https://github.com/plone/Products.CMFPlone/issues/2315>_.
  [ajung]


5.1.4.rc1 (2018-09-30)
----------------------

New features:

- Upgrade grunt + plugins to same versions as in
  mockup https://github.com/plone/mockup/pull/870
  [sunew]

- Include TinyMCE 4.7.13
  [erral]

- Update mockup to latest version.
  [frapell]


Bug fixes:

- Remove the devdependencies from bower.json - they are just used for running tests in mockup, not here.
  [sunew]

- Let the ``combine-bundles`` import step also work when the ``IBundleRegistry`` keyword is not in ``registry.xml``, but in a ``registry`` directory.
  `Issue 2520 <https://github.com/plone/Products.CMFPlone/issues/2502>`_.
  [maurits]

- Get rid of obsolete ``X-UA-Compatible`` header.
  [hvelarde]

- Fix registration of ``robots.txt`` browser view to avoid ``AttributeError`` on Zope's root (fixes `#2052 <https://github.com/plone/Products.CMFPlone/issues/2052>`_).
  [hvelarde]

- Fixed tests when IRichText behavior is used.
  IRichText -> IRichTextBehavior
  This is a follow up to `issue 476 <https://github.com/plone/plone.app.contenttypes/issues/476>`_.
  [iham]
- Fix plone.app.redirector support for JSON/unspecified requests.
  [rpatterson]

- Do not include too new upgrades when upgrading Plone Site.
  Otherwise the Plone Site ends up at a newer version that the filesystem code supports,
  giving an error when upgrading, and resulting in possibly missed upgrades later.
  Fixes `issue 2377 <https://github.com/plone/Products.CMFPlone/issues/2377>`_.
  [maurits]

- Add test for issue #2469.
  [jensens]

- Fix toolbar on mobile:
    - Clicking on menu links, submenus are not shown
    - With a opened submenu, html has huge margins and page content disappears
  [nzambello]

- Remove last legacy Javascript ``highlight-searchterms.js``.
  Removes also the skins folder ``plone_ecmascript``.
  It was broken for almost all use cases (Google, other search engines, own live search);
  JS worked only when coming from Plone detailed search page.
  [jensens]

- Fix failing thememapper robot test after rebuild of thememapper bundle in p.a.theming PR 147
  [sunew]

- Fix Datatables CSS not available #2512 via PR mockup #863
  [sunew, thet]


5.1.3 (2018-06-22)
------------------

Breaking changes:

- 'registered' template from portal_skins' portal_login has been moved to plone.app.users as a browser view.
  [jensens]

New features:

- Optional auto-login after passwort (re-)set.
  Active if registry key `plone.autologin_after_password_reset` is `True`.
  [jensens, agitator]

Bug fixes:

- Hide ``plone.app.querystring`` from add-ons control panel.
  Fixes `issue 2426 <https://github.com/plone/Products.CMFPlone/issues/2426>`_.
  [maurits]

- Fix https://github.com/plone/Products.CMFPlone/issues/2394, error on login after password reset.
  [jensens, agitator]

- Do not include too new upgrades when upgrading Plone Site.
  Otherwise the Plone Site ends up at a newer version that the filesystem code supports,
  giving an error when upgrading, and resulting in possibly missed upgrades later.
  Fixes `issue 2377 <https://github.com/plone/Products.CMFPlone/issues/2377>`_.
  [maurits]

- After site creation, do not render the add-site template: we redirect anyway.
  [maurits]


- Unflakied a unit test.
  [Rotonen]


5.1.2 (2018-04-08)
------------------

New features:

- Enhanced output of Advanced Catalog Clear And Rebuild feature.
  Better logging with progress and number of objects before and after.
  [jensens]

Bug fixes:

- Fixed bug in ajax standard_error_message.  [djay, maurits]

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

- Change in TinyMCE css location so bundles can be built without errors
  Fixes `issue 2359 <https://github.com/plone/Products.CMFPlone/issues/2359>`_.
  [frapell]


5.1.1 (2018-03-10)
------------------

Bug fixes:

- Include TinyMCE 4.7.6
  [frapell]


5.1.0.1 (2018-02-14)
--------------------

New features:

- Mockup update.
  [thet]

Bug fixes:

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

- Fixed linkintegrity robot tests.  [maurits]

- Fixed flaky actions controlpanel tests by waiting longer.  [maurits]

- Require AccessControl 3.0.14 so ``guarded_getitem`` is used.
  Part of PloneHotfix20171128.  [maurits]

- Improved isURLInPortal according to PloneHotfix20171128.
  Accept only http/https, and doubly check escaped urls.  [maurits]

- Fixed Products.CMFPlacefulWorkflow being marked as not installed after upgrade from 4.3.
  This is true for any package in the Products namespace that was installed.
  Fixes `issue 2103 <https://github.com/plone/Products.CMFPlone/issues/2103>`_.
  [maurits]


5.1.0 (2018-02-05)
------------------

New features:

- Release Plone 5.1
  [esteele]


5.1rc2 (2017-11-26)
-------------------

New features:

- Toolbar: Allow configuration of the toolbar and submenu width via pattern variables.
  [thet]

- Update npm dependencies.
  [thet]

Bug fixes:

- Show example for expression in actions control panel.
  [maurits]

- Fixed add-on listed as uninstalled when the default profile is not the first alphabetically.
  Fixes `issue 2166 <https://github.com/plone/Products.CMFPlone/issues/2166>`_.
  [maurits]

- Less variables: Fix calculation of screen max sizes.
  Max sizes were two pixels too high.
  [thet]

- Mockup update.
  [thet]

- Remove site path from path in show_inactive in catalog search
  [Gagaro]

- Don't raise Unauthorized on show_inactive check in catalog search
  [tomgross]

- Bump metadata.xml version.
  [thet]

- Extract CMFDefault specific config from `meta.zcml` into `meta-bbb.zcml`
  to allow AT free and AT included sites.
  [tomgross]

- Add basic tests for all main zmi management screens.
  [pbauer]

- Fixes #2105: how to get ``email_from_name`` information in sendto_form.
  [cekk]

5.1rc1 (2017-09-10)
-------------------

Breaking changes:

- Replaced cssmin with PyScss to ensure Python 3 compatibility and maintainability.
  Removed dependency to cssmin, so could break dependency for third party addons that depend on it.
  Introduced PyScss as a drop in replacement that could also do more things.
  Discussion on that at https://github.com/plone/Products.CMFPlone/issues/1800
  [loechel]

- Fix and migrate safe_html filter completly into Plone registry and sync settings with TinyMCE.
  Also some unused options in controlpanel where removed, like stripped_combinations and class_blacklist.
  [MrTango]

New features:

- Update ``plone-legacy-compiled.js`` and ``plone-legacy-compiled.css``.
  [thet]

- Update mockup to latest version.
  [thet]

- Added ``Show Toolbar`` permission.
  [agitator]

- Add RobotFramework screenshot tests for the Plone documentation.
  [datakurre, polyester]

- Add jqtree-contextmenu to the resource registry
  [b4oshany]

- Add js-shortcuts to the resource registry
  [b4oshany]

Bug fixes:

- Recover missing dashboard (user actions)
  https://github.com/plone/Products.CMFPlone/issues/1132
  [fgrcon]

- Remove the right padding on toolbar submenu entries.
  That looked a bit weird.
  [thet]

- Fixed accidentally removing permissions when saving the ``portal_controlpanel`` settings in the ZMI.
  Fixes `issue 1376 <https://github.com/plone/Products.CMFPlone/issues/1376>`_.  [maurits]

- Do not open links on a new tab as this is against basic usability guidelines.
  [hvelarde]

- add :focus class on toolbar for keyboard users  (https://github.com/plone/Products.CMFPlone/issues/1620)
  [polyester]

- Fix empty DX add_forms if formlib is also installed thru addon dependencies
  [MrTango]

- Update TinyMCE links (tinymce-controlpanel) to https
  [svx]

- Fix ``utils.get_top_site_from_url`` to work with non-OFS contexts.
  [thet]

- remove mention of "retina" (https://github.com/plone/Products.CMFPlone/issues/2123)
  [tkimnguyen]


5.1b4 (2017-07-03)
------------------

New features:

- Integrate ``mockup-patterns-structureupdater`` for updating title and description depending on the current context on the folder contents page.
  [thet]

- Updated jqtree to 1.4.1 from 1.3.3
  [b4oshany]

- Update mockup to latest version.
  [thet]

- add registry settings for thumb and icon handling  in tables, lists and portlets
  https://github.com/plone/Products.CMFPlone/issues/1734 (PLIP)
  recompiled bundle plone-logged-in
  requires upgrade step (reapply profile)
  [fgrcon]

- Update mockup to latest version.
  [thet]

- new metadata catalog column mime_type
  https://github.com/plone/Products.CMFPlone/issues/1995
  [fgrcon]

- Include TinyMCE 4.5.6
  [frapell]

Bug fixes:

- Use explicit @@footer view for footer portlet.
  [agitator]

- Translate image scales in patterns.
  [Gagaro]

- Gruntfile generation no longer fails on introspecting resourceDirectory
  configurations using a plone.browserlayer layer, by loading all layers
  configured for the site used during generation.
  Fixes Issue `#2080`.
  [seanupton]

- fixed css-classes for thumb scales ...
  https://github.com/plone/Products.CMFPlone/issues/2077
  [fgrcon]

- Fix current value in group details edit form.
  [Gagaro]

- Fixed KeyError ``productname`` when there is a broken add-on in the add-ons control panel.
  Fixes `issue 2065 <https://github.com/plone/Products.CMFPlone/issues/2065>`_.
  [maurits]

- Fix ``test_tinymce.robot`` test to work with latest related items changes.
  [thet]

- Fix expiration date when displaying in registered form.
  [allusa]

- Remove TinyMCE pattern options from the body, as these are always set on the richtext fields mimetype selector or - if not there - on the textfield itself.
  Refs: https://github.com/plone/Products.CMFPlone/pull/2059
  [thet]

- Let TinyMCE options for the related items widget be generated by ``plone.app.widgets.utils.get_relateditems_options``.
  This aligns the options to how the related items widget is used elsewhere.
  Fixes https://github.com/plone/Products.CMFPlone/issues/1974
  [thet]

- CMFCore ``WarningInterceptor`` test base class was gone and is not needed in Plone, so removed.
  [jensens]

- Fix default value for ``robots.txt`` to avoid issues with content containing "search" in the id.
  [hvelarde]

- Remove references to Products.CMFDefault on meta.zcml
  [gforcada]

- Adapt tests to render social metadata only if you are anonymous.
  [bsuttor]

- Fix search term munging with queries that include and, or and not.
  [malthe]

- Fix issue where catalog search with path failed when path had inaccessible
  (private) levels
  [datakurre]

- Add constraint to avoid filling ``twitter_username`` field with strings starting with a "@" character.
  [hvelarde]

- Fixed addons/donations links, removed dead "add your site" link
  [sgrepos]

- Fix isssue where collapsed toolbar was not initialized properly on page
  refresh, resulting wide blank space between collapsed toolbar and page
  content
  [datakurre]

- Removed "change portal events" permission
  [kakshay21]

- Updated dead link to the error reference docs
  [sgrepos]

- Do not rely on order in test of generated body classes ``browser.txt``.
  [jensens]

- Fix possible ``mechanize.AmbiguityError`` in controlpanel tests.
  [jensens]

5.1b3 (2017-04-03)
------------------

New features:

- Adapt code and tests to the new indexing operations queueing.
  Part of PLIP 1343: https://github.com/plone/Products.CMFPlone/issues/1343
  [gforcada]

- Make use of plone.namedfile's tag() function to generate img tags. Part of plip 1483.
  [didrix]

- Add retina scales settings in image handling. Part of plip 1483
  [didrix]

Bug fixes:

- Use canonical url instead of absolute url for RSS feed items.
  This code is used for the social viewlet too.
  So default pages are reported with their parent url.
  Fixes `layout issue 118 <https://github.com/plone/plone.app.layout/issues/118>`_.
  [maurits]

- Fix social media schema field types of ``twitter_username``, ``facebook_app_id`` and ``facebook_username`` to be ``ASCIILine`` instead of ``TextLine``.
  [hvelarde]

- Show version of products in Add-ons control panel configlet.
  This fixes https://github.com/plone/Products.CMFPlone/issues/1472.
  [hvelarde]

- Resource registry legacy bundle cooking: Exit early with a warning, if preconditions to build are not given (no compilation paths).
  Allow cooking CSS, even if no JS is defined.
  Log all important steps of the cooking process.
  [thet]

- Remove unused ``plone.css`` from static repository.
  [thet]

- Check for ``AccessInactivePortalContent`` for each path in a catalog query.
  This solves a problem, where Editors couldn't see inactive content, even though they had the required permission on a subpath of the portal (e.g. a subsite).
  [thet]

- Test: Wrong use of assertTrue in testResourceRegistries.
  [jensens]

- Fix issue popped iup after fix of use of assertTrue in testResourceRegistries: insert-before in legacy resource import was broken.
  [jensens]


5.1b2 (2017-02-20)
------------------

Bug fixes:

- Fix packaging error.
  [esteele]

5.1b1 (2017-02-20)
------------------

Breaking changes:

- Add helper method to get all catalog entries from a given catalog: ``Products.CMFPlone.CatalogTool.catalog_get_all``.
  In Products.ZCatalog before 4.0 a catalog call without a query returned all catalog brains.
  This can be used as a replacement where it is needed, for exampe in tests.
  [thet, gogobd]

- Remove ``query_request`` from CatalogTool's search method, as it isn't supported in Products.ZCatalog 4 anymore.
  [thet]

- Removed our patch that added ``secureSend`` to the ``MailHost``.
  This was originally scheduled for removal in Plone 5.0.  See `issue
  965 <https://github.com/plone/Products.CMFPlone/issues/965>`_.
  [maurits]

- The related items widget has changed a lot.
  See the Mockup changelog for 2.4.0 here: https://github.com/plone/mockup/blob/master/CHANGES.rst

- All css classes named ``enableUnloadProtection`` were changed to ``pat-formunloadalert`` to trigger that pattern.
  Templates using ``enableUnloadProtection`` should change to ``pat-formunloadalert`` too.
  This change shouldn't impact too much, because the form unload protection didn't work at all in Plone 5 until now.
  [thet]

- MimetypesRegistry icons are now a browser resource directory instead of skins folder.
  [jensens]

- Remove unused ``plone_scripts`` (not used nor tested anywhere in coredev) [jensens, davisagli]

    - ``add_ext_editor.py``
    - ``author_find_content.py``
    - ``canSelectDefaultPage.py`` with tests
    - ``create_query_string.py``
    - ``createMultiColumnList.py``
    - ``displayContentsTab.py``
    - ``formatColumns.py`` with tests
    - ``getAllowedTypes.py``
    - ``getGlobalPortalRoles.py``
    - ``getNotAddableTypes.py``
    - ``getPopupScript.py``
    - ``getPortalTypeList.py`` and metadata
    - ``getPortalTypes.py``
    - ``getSelectableViews.py`` with tests
    - ``hasIndexHtml.py`` with tests
    - ``navigationParent.py`` with test
    - ``plone_log.py``
    - ``plone.css.py``
    - ``returnNone.py`` with occurence refactored
    - ``reverseList.py`` with test
    - ``sort_modified_ascending.py``

- Move scripts ``datecomponents.py`` and ``show_id.py`` to Archetypes
  [jensens, davisagli]

- Remove methods of the ``@@plone`` view that were marked for deprecation:
  - ``showEditableBorder`` (use ``@@plone/showToolbar``)
  - ``mark_view`` (use ``@@plone_layout/mark_view``)
  - ``hide_columns`` (use ``@@plone_layout/hide_columns``)
  - ``icons_visible`` (use ``@@plone_layout/icons_visible``)
  - ``getIcon`` (use ``@@plone_layout/getIcon``)
  - ``have_portlets`` (use ``@@plone_layout/have_portlets``)
  - ``bodyClass`` (use ``@@plone_layout/bodyClass``)
  [davisagli]

- Move plone_content skin templates into Products.ATContentTypes as browser views.
  [gforcada]

New features:

- Added ``ok`` view.  This is useful for automated checks, for example
  httpok, to see if the site is still available.  It returns the text
  ``OK`` and sets headers to avoid caching.
  [maurits]

- Make contact form extensible. This fixes https://github.com/plone/Products.CMFPlone/issues/1879.
  [timo]

- Don't minify CSS or JavaScript resources if they end with ``.min.css`` resp. ``.min.js``.
  [thet]

- Add ``safe_encode`` utility function to ``utils`` to safely encode unicode to a specified encoding.
  The encoding defaults to ``utf-8``.
  [thet]

- The password reset templates were changed to make use of ``content-core`` macros.
  [thet]

- Add utility method to retrieve the top most parent request from a sub request.
  [thet]

- Add ``mockup-patterns-relateditems-upload`` resource, which can be used in custom bundles to add the upload feature in the related items widget.
  [thet]

- Move ``get_top_site_from_url`` from plone.app.content to ``utils.py`` and make it robust against unicode paths.
  This function allows in virtual hosting environments to acquire the top most visible portal object to operate on.
  It is used for example to calculate the correct virtual root objects for Mockup's related items and structure pattern.
  [thet]

- Add sort_on field to search controlpanel.
  [rodfersou]

- PLIP 1340: Deprecate portal_quickinstaller.
  You should no longer use CMFQuickInstallerTool methods, but GenericSetup profiles.
  See https://github.com/plone/Products.CMFPlone/issues/1340
  [maurits]

- Include mockup 2.4.0.
  [thet]

- PasswordResetTool moved from its own package to here (includes cleanup and removal of ``getStats``).
  [tomgross]

- Prevent workflow menu overflowing in toolbar [MatthewWilkes]

- Add default icon for top-level contentview and contentmenu toolbar entries [alecm]

- Toolbar: Make menu hover background fit whole menu width. [thet]

- Toolbar: Don't force scoll buttons to be left, when toolbar is right. [thet]

- Toolbar: Make first level list items exand the whole toolbar width - also when scroll buttons are shown. [thet]

- Toolbar: Make scroll buttons exand whole toolbar width. [thet]

- Toolbar: Let the toolbar submenus be as wide as they need to be and do not break entries into multiple lines. [thet]

- Resource Registry:
  In ``debug-mode`` (zope.conf, buildout) do not load cache the production bundle.
  [jensens]

- Resource Registry:
  In ``debug-mode`` (zope.conf, buildout) do not ignore development mode for anonymous users.
  [jensens]

- Resource Registry: If file system version is newer than ``last_compilation`` date of a bundle, use this as ``last_compilation`` date.
  [jensens]

- Simplify generated Gruntfile.js (DRY)
  [jensens]

- Fix: Do not modify the Content-Type header on bundle combine.
  [jensens]


Bug fixes:


- Moved getToolByName early patch to the later patches.
  This fixes a circular import.
  See `issue #1950 <https://github.com/plone/Products.CMFPlone/issues/1950>`_.
  [maurits]

- Include JS Patterns when loading a page via ajax or an iframe [displacedaussie]

- Restore ability to include head when loading via ajax [displacedaussie]

- Added security checks for ``str.format``.  Part of PloneHotfix20170117.  [maurits]

- Fixed workflow tests for new ``comment_one_state_workflow``.  [maurits]

- Fixed sometimes failing search order tests.  [maurits]

- Load some Products.CMFPlone.patches earlier, instead of in our initialize method.
  This is part of PloneHotfix20161129.
  [maurits]

- Depend on CMFFormController directly, because our whole login process is based on it and its installed in the GenericSetup profile.
  Before it was installed indeirectly due to a dependency in some other package which is gone.
  [jensens]

- Fix Search RSS link condition to use search_rss_enabled option and use
  rss.png instead of rss.gif that doesn't exist anymore.
  [vincentfretin]

- Fix potential KeyError: admin in doSearch in Users/Groups controlpanel.
  [vincentfretin]

- Let the ``mail_password_template`` and ``passwordreset`` views retrieve the expiry timeout from the view, in hours.
  [thet]

- Fix i18n of the explainPWResetTool.pt template.
  [vincentfretin]

- Remove "Minimum 5 characters" in help_new_password in pwreset_form.pt like
  in other templates.
  [vincentfretin]

- Fix duplicate i18n attribute 'attributes' in controlpanel/browser/actions.pt
  [vincentfretin]

- Use "site administration" in lower case in accessibility-info.pt and
  default_error_message.pt like in other templates.
  [vincentfretin]

- Support adding or removing bundles and resources on a request when working with resource tiles in a subrequest.
  [thet]

- Remove jquery.cookie from plone-logged-in bundle's stub_js_modules.
  The toolbar, which has a dependency on jquery.cookie,
  was moved from the plone bundle to plone-logged-in in CMPlone 5.1a2.
  [thet]

- Fix various layout issues in toolbar [alecm]

- Style display menu headings differently from actions [alecm]

- Avoid dependency on plone.app.imaging. [davisagli]

- Fix TinyMCE table styles [vangheem]

- Fix TinyMCE content CSS support to allow themes to define
  external content CSS URLs (as with CDN like setup).
  [datakurre]


- Add utf8 headers to all Python source files. [jensens]

- Add default icon for top-level contentview and contentmenu toolbar entries [alecm]
- Reset and re-enable ``define`` and ``require`` for the ``plone-legacy`` bundle in development mode.
  Fixes issues with legacy scripts having RequireJS integration in development mode.
  In Production mode, resetting  and re-enabling is done in the compiled bundle.
  [thet]

- Apply security hotfix 20160830 for ``z3c.form`` widgets.  [maurits]

- Fixed tests in combination with newer CMFFormController which has the hotfix.  [maurits]

- Apply security hotfix 20160830 for ``@@plone-root-login``.  [maurits]

- Apply security hotfix 20160830 for ``isURLInPortal``.  [maurits]

- Enable unload protection by using pattern class ``pat-formunloadalert`` instead ``enableUnloadProtection``.
  [thet]

- Provide the image scale settings in TinyMCE image dialog.
  [thet]

- Fix link on ``@@plone-upgrade``
  [gforcada]

- Remove LanguageTool layer.
  [gforcada]

- Use fork of grunt-sed which is compatible with newer grunt version.
  [gforcada]

- Move some tests from ZopeTestCase to plone.app.testing.
  [gforcada, ivanteoh, maurits]

- wording changes for social media settings panel
  [tkimnguyen]

- URL change for bug tracker, wording tweaks to UPGRADE.txt
  [tkimnguyen]

- Cleanup code of resource registry.
  [jensens]

- Fix plone-compile-resources:
  Toolbar variable override only possible if prior defined.
  Define ``barcelonetaPath`` if ``plonetheme.barceloneta`` is available (but not necessarily installed).
  [jensens]

- Include inactive content in worklists.  [sebasgo]

- Fix #1846 plone-compile-resources: Missing Support for Sites in Mountpoints
  [jensens]

- Do not use unittest2 (superfluos since part of Python 2.7).
  [jensens]

- Fix security test assertion:
  TestAttackVectorsFunctional test_widget_traversal_2 assumed a 302 http return code when accessing some private API.
  Meanwhile it changed to return a 404 on the URL.
  Reflect this in the test and expect a 404.
  [jensens]

- Fix atom.xml feed not paying attention for setting to show about information
  [vangheem]

- Fix imports from package Globals (removed in Zope4).
  [pbauer]

- Skip one test for zope4.
  [pbauer]

- Fix csrf-test where @@authenticator was called in the browser.
  [pbauer]

- Do not attempt to wrap types-controlpanel based on AutoExtensibleForm and
  EditForm in Acquisition using __of__ since
  Products.Five.browser.metaconfigure.simple no longer has
  Products.Five.bbb.AcquisitionBBB as a parent-class and thus no __of__.
  Anyway __of__ in AcquisitionBBB always only returned self since
  Products.Five.browser.metaconfigure.xxx-classes are always aq-wrapped
  using location and __parent__. As a alternative you could use
  plone.app.registry.browser.controlpanel.ControlPanelFormWrapper as
  base-class for a controlpanel since ControlPanelFormWrapper subclasses
  Products.Five.BrowserView which again has AcquisitionBBB.
  [pbauer]

- Remove eNotSupported (not available in Zope 4)
  [tschorr]

- Remove deprecated __of__ calls on BrowserViews
  [MrTango]

- Test fix (Zope 4 related): More General test if controlpanel back link URL is ok.
  [jensens]


5.1a2 (2016-08-19)
------------------

Breaking changes:

- Move toolbar resources to plone-logged-in bundle and recompile bundles.
  [davilima6]

- Don't fail, if ``timestamp.txt`` was deleted from the resource registries production folder.
  [thet]

- Add ``review_state`` to ``CatalogNavigationTabs.topLevelTabs`` results.
  This allows for exposing the items workflow state in portal navigation tabs.
  [thet]

- Remove discontinued module ``grunt-debug-task`` from ``plone-compile-resources``.
  [jensens]

- Remove deprecated resource registrations for ``mockup-parser`` and ``mockup-registry`` from mockup-core.
  Use those from patternslib instead.
  [thet]

- ``plone-compile-resources``: Install ``grunt-cli`` instead of depending on an installed ``grunt`` executable.
  If you already have a auto-generated ``package.json`` file in buildout directory, remove it.
  [thet]


- Moved code around and deprecated old locations in ``Products/CMFPlone/patterns/__init__``.
  This goes together with same pattern settings changes in ``plone.app.layout.globals.pattern_settings``.
  Also moved general usable ``./patterns/utils/get_portal`` to ``./utils/.get_portal``.
  Deprecated ``./patterns/utils/get_portal`` and ``./patterns/utils/get_portal``.
  [jensens]


New features:

- Updated components directory, recompiled bundles.
  [thet]

- Align bower components with newest mockup + documentation updates on mockup update process.
  [thet]

- Ignore a bit more in ``.gitignores`` for CMPlones bower components.
  [thet]

- Added setting to editing controlpanel to enable limit of keywords to the current navigation root.
  [jensens]

- Make login modal dialog follow any redirects set while processing the login request.
  [fulv]

- Add link to training.plone.org
  [svx]

- Allow to define multiple ``tinymce-content-css`` in theme ``manifest.cfg`` files, seperated by a comma.
  [thet]

- Update npm package depencies.
  [thet]

- Supported ``remove`` keyword for configlets in controlpanel.xml.  [maurits]

- Deprecated Gruntfile generation script ``plone-generate-gruntfile``.
  Modified the ``plone-compile-resources`` script to support more parameters in order to take over that single task too.
  Also clean up of parameters, better help and refactored parts of the code.
  [jensens]

- Make filter control panel work with new version of safe HTML transform
  [tomgross]
- Allow to hide/show actions directly from the Actions control panel list
  [ebrehault]


Bug fixes:

- Have more patience in the thememapper robot test.
  [maurits]

- Upgrade ``less-plugin-inline-urls`` to ``1.2.0`` to properly handle VML url node values in CSS.
  [thet]
- Fixed adding same resource/bundle to the request multiple times.
  [vangheem]

- Fixed missing keyword in robot tests due to wrong documentation lines.
  [maurits]

- TinyMCE default table styles were broken after install due to a wrong default value.
  [jensens]

- Rewording of some Site control panel text [tkimnguyen]

- Fixed syntaxerror for duplicate tag in robot tests.  [maurits]

- Marked two robot tests as unstable, non-critical.
  Refs https://github.com/plone/Products.CMFPlone/issues/1656  [maurits]

- Use ``Plone Test Setup`` and ``Plone Test Teardown`` from ``plone.app.robotframework`` master.  [maurits]

- Let npm install work on windows for plone-compile-resources.
  [jensens]

- Don't fail, when combining bundles and the target resource files (``BUNLDE-compiled.[min.js|css]``) do not yet exist on the filesystem.
  Fixes GenericSetup failing silently on import with when a to-be-compiled bundle which exists only as registry entry is processed in the ``combine-bundle`` step.
  [thet]

- Workaround a test problem with outdated Firefox 34 used at jenkins.plone.org.
  This Workaround can be removed once https://github.com/plone/jenkins.plone.org/issues/179 was solved.
  [jensens]

- Fix select2 related robot test failures and give the test_tinymce.robot scenario a more unique name.
  [thet]

- Add missing ``jquery.browser`` dependency which is needed by patternslib.
  [thet]

- Toolbar fixes:
  - Autoformat with cssbrush and js-beautify,
  - Remove ``git diff`` in line 105, which broke compilation.
  - Use patternslib ``pat-base`` instead of ``mockup-patterns-base``.
  - Remove dependency on deprecated ``mockup-core``.
  [thet]

- Removed docstrings from PropertyManager methods to avoid publishing them.  [maurits]

- Added publishing patch from Products.PloneHotfix20160419.
  This avoids publishing some methods inherited from Zope or CMF.  [maurits]

Fixes:

- Remove whitespaces in ``Products/CMFPlone/browser/templates/plone-frontpage.pt``.
  [svx]

- Fixed versioning for File and Image.
   [iham]

- Do not hide document byline viewlet by default;
  it is controled by the `Allow anyone to view 'about' information` option in the `Security Settings` of `Site Setup` (closes `#1556`_).
  [hvelarde]

- Removed docstrings from some methods to avoid publishing them.  From
  Products.PloneHotfix20160419.  [maurits]

- Fix issue where incorrectly configured formats would cause TinyMCE to error
  [vangheem]

- Closes #1513 'Wrong portal_url used for TinyMCE in multilingual site',
  also refactors the patterns settings and cleans it up.
  [jensens]

- Removed inconsistency in the display of `Site Setup` links under 'Users and Groups'
  control panel.
  [kkhan]

- Only encode JS body if unicode in gruntfile generation script to avoid
  unicode error.
  [jensens]

- Only encode CSS body if unicode in gruntfile generation script to avoid
  unicode error.
  [rnix]

- Gruntfile failed if only css or only javascripts were registered.
  [jensens]

- Bundle aggregation must use ++plone++static overrided versions if any.
  [ebrehault]

- Fix bundle aggregation when bundle has no CSS (or no JS)
  [ebrehault]

- Fix relative url in CSS in bundle aggregation
  [ebrehault]

- Do not hard-code baseUrl in bundle to avoid bad URL when switching domains.
  [ebrehault]

- fix typo and comma splice error in HTML filtering control panel [tkimnguyen]

- Use zope.interface decorator.
  [gforcada]

- Remove advanced_search input which is in double.
  [Gagaro]


5.1a1 (2016-03-31)
------------------

Incompatibilities:

- Changed these ``section`` elements to ``div`` elements: ``#viewlet-above-content``, ``#viewlet-above-content-body``, ``#content-core``, ``#viewlet-below-content-body``.
  And these portlets ``section`` elements to ``aside`` elements: ``#portal-colophon``, ``#portal-footer-signature``.
  This might affect your custom styling or javascript.
  [maurits]

New:

- Upgrade to tinymce to 4.3.4
  [vangheem]

- For the controlpanel portlets, use the nearest site url as a base for the overview-controlpanel.
  This gives more flexibility for sub site controlpanels.
  [thet]

- added invisible-grid table styles
  [agitator]

- Control panel to mange portal actions
  [ebrehault]

- new less variable to configure the width of the toolbars submenu called ``plone-toolbar-submenu-width``.
  [jensens]

- new zcml feature "plone-51" added. Profile version set to 5101.
  Version references set to 5.1.0.
  [jensens]

- Registered post_handler instead of plone-final.  The plone-final
  import step now does nothing.  Instead, we redefined the old handler
  as a post_handler explicitly for our main profile.  This is
  guaranteed to really run after all other import steps, which was
  never possible in the old way.  The plone-final step is kept for
  backwards compatibility.
  [maurits]

- Remove Zope mention in logout form
  [tkimnguyen]

- Do not encode reply-to email address for contact-info form
  [tkimnguyen]

Fixes:

- Fixed displaying the body text of a feed item.  This is when
  ``render_body`` is switched on in the Syndication settings.
  [maurits]

- Make Gruntfile.js generation script a bit more verbose to show the effective
  locations of the generated bundles. This helps in case of non-working setups
  also as if bundle compilation was started in browser at a first run a and
  next run was run using the script and files were generated at different
  places than expected.
  [jensens]

- Ensured front-page is English when creating an English site.
  Previously, when creating an English site with a browser that
  prefers a different language, the body text ended up being in the
  browser language.  For languages without a front-page text
  translation the same happened: they got the other language instead
  of English.  [maurits]

- Fixed test error in ``test_controlpanel_site.py`` failed with random error.
  [jensens]

- Do not break background images relative urls in CSS when concatening bundles
  [ebrehault]

- Fixed html validation: element nav does not need a role attribute.
  [maurits]

- Fixed html validation: section lacks heading.
  [maurits]

.. _`#950`: https://github.com/plone/Products.CMFPlone/issues/950
.. _`#952`: https://github.com/plone/Products.CMFPlone/issues/952
.. _`#963`: https://github.com/plone/Products.CMFPlone/issues/963
.. _`#991`: https://github.com/plone/Products.CMFPlone/issues/991
.. _`#996`: https://github.com/plone/Products.CMFPlone/issues/996
.. _`#1015`: https://github.com/plone/Products.CMFPlone/issues/1015
.. _`#1041`: https://github.com/plone/Products.CMFPlone/issues/1041
.. _`#1053`: https://github.com/plone/Products.CMFPlone/issues/1053
.. _`#1232`: https://github.com/plone/Products.CMFPlone/issues/1232
.. _`#1255`: https://github.com/plone/Products.CMFPlone/issues/1255
.. _`#1556`: https://github.com/plone/Products.CMFPlone/issues/1556
