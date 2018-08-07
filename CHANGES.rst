.. This file should contain the changes for the last release only, which
   will be included on the package's page on pypi. All older entries are
   kept in HISTORY.txt

Changelog
=========

5.2a1 (unreleased)
------------------

Breaking changes:

- Remove all dependencies on plone.app.controlpanel. 
  Third party code need either to depend on plone.app.controlpanel 4.0,
  which is a backward compatibilit package only, or also update to not depend on it anymore.
- *add item here*

New features:

- Adapt code and tests to the new indexing operations queueing.
  Part of PLIP 1343: https://github.com/plone/Products.CMFPlone/issues/1343
  [gforcada]

Bug fixes:

- Show version of products in Add-ons control panel configlet.
  This fixes https://github.com/plone/Products.CMFPlone/issues/1472.
- Remove last legacy Javascript ``highlight-searchterms.js``. 
  Removes also the skins folder ``plone_ecmascript``. 
  It was broken for almost all use cases (Google, other search engines, own live search);
  JS worked only when coming from Plone detailed search page.
  [jensens]

- Get rid of obsolete ``X-UA-Compatible`` header.
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

- Remove last legacy Javascript ``highlight-searchterms.js``. 
  Removes also the skins folder ``plone_ecmascript``. 
  It was broken for all (Google, other search engines, own live search);
  JS worked only when coming from Plone detailed search.
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

- New browser view based login code - merged from plone.login (credits to esteele, pbauer, agitator, jensens, et al).
  `portal_skins/plone_login` is now gone, see PLIP #2092.
  Also, password reset view moved to login subfolder to keep things together.
  Some testbrowser based tests needed changes because of z3c.form based login form .
  The Plone specific, rarely used cross site __ac cookie SSO feature/hack was removed.
  In case somebody needs this, please make it an addon package.
  Better use a field proven, more secure way, like OAuth2, Shibboleth or someting similar.
  [jensens, et al]

- Adapt tests to `Products.GenericSetup >= 2.0` thus requiring at least that
  version.
  [icemac]

- Some tools from CMFCore are now utilities
  [pbauer]

Bug fixes:

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


5.1.3 (2018-06-22)
------------------

Breaking changes:

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
