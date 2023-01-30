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

5.2.11 (2023-01-30)
-------------------

Bug fixes:


- Prepare release 5.2.11.
  No changes compared to release candidate.
  [maurits] (#5211)


5.2.11rc1 (2023-01-26)
----------------------

Bug fixes:


- During login, when login_time is invalid, warn and reset it to 2000/01/01.
  Fixes `issue 3656 <https://github.com/plone/Products.CMFPlone/issues/3656>`_.
  [maurits] (#3656)
- When autologin after password reset is enabled, use the same adapters as during normal login.
  Specifically: the ``IInitialLogin`` and ``IRedirectAfterLogin`` adapters.
  Autologin is enabled by default.
  Fixes `issue 3713 <https://github.com/plone/Products.CMFPlone/issues/3713>`_.
  [maurits] (#3713)
- Update metadata version to 5219, Plone 5.2.11.
  [maurits] (#5219)


5.2.10 (2022-10-31)
-------------------

Bug fixes:


- Fixed an issue that prevented the user to select the preferred timezone (#1290)
- Fixed adding control panel action via ZMI.
  [maurits] (#1959)
- Set portal title in registry when creating a new Plone site
  [erral] (#3584)
- Change test to make sure email is sent in utf-8
  [erral] (#3588)
- Update metadata version to 5218, Plone 5.2.10.
  [maurits] (#5218)


5.2.9 (2022-07-21)
------------------

Bug fixes:


- Prepare release 5.2.9.
  No changes compared to release candidate.
  [maurits] (#529)


5.2.9rc1 (2022-07-18)
---------------------

Bug fixes:


- Update metadata version to 5217, Plone 5.2.9.
  [maurits] (#5217)


5.2.8 (2022-05-14)
------------------

Bug fixes:


- Prepare release 5.2.8.

  No changes compared to release candidate. (#528)


5.2.8rc1 (2022-04-29)
---------------------

Bug fixes:


- Update WCAG version to 2.1 in the accessebility-info default content.
  [marwanatef2] (#3273)
- Remove date range search fix, which was done in Products.ZCatalog.
  [wesleybl] (#3432)
- Fix detection of initial login time [MrTango] (#3447)
- Update metadata version to 5216, Plone 5.2.8.
  [maurits] (#5216)


5.2.7 (2022-01-28)
------------------

Bug fixes:


- Release Plone 5.2.7 final.
  No changes compared to last release candidate.
  [maurits] (#3413)


5.2.7rc1 (2022-01-25)
---------------------

Bug fixes:


- Add plone.synchronize as dependency, because plone.dexterity 2.10.5 has removed this dependency.
  Core Plone does not need the package anymore, but in case someone uses it, it is not nice to lose it in a bugfix release of Plone.
  [maurits] (#157)
- The portal catalog will not try to index itself anymore [ale-rt] (#3312)
- Load adapter for index location, only if Archetypes is installed. [wesleybl] (#3347)
- Add missing lxml dependency [MrTango] (#3356)
- Update metadata version to 5215, Plone 5.2.7.
  [maurits] (#5215)


5.2.6 (2021-10-22)
------------------

Bug fixes:


- Release Plone 5.2.6 final.
  No changes compared to last release candidate. (#3336)


5.2.6rc1 (2021-10-16)
---------------------

Bug fixes:


- Update metadata version to 5214, Plone 5.2.6.
  [maurits] (#5214)


5.2.5 (2021-08-06)
------------------

Bug fixes:


- Release Plone 5.2.5 final.
  No changes compared to last release candidate.
  [maurits] (#3292)


5.2.5rc1 (2021-07-31)
---------------------

New features:


- Add PLONE52MARKER Python marker
  [sneridagh] (#3257)


Bug fixes:


- Removed the docstring from various methods to avoid making them available via a url.
  From the `Products.PloneHotfix20210518 reflected XSS fix <https://plone.org/security/hotfix/20210518/reflected-xss-in-various-spots>`_.
  [maurits] (#3274)
- Add the remote code execution fix from the `Products.PloneHotfix20210518 expressions patch <https://plone.org/security/hotfix/20210518/remote-code-execution-via-traversal-in-expressions>`_.
  We need this because Zope 4.6.2 is too strict for us.
  [maurits] (#3274)


5.2.4 (2021-03-03)
------------------

Bug fixes:


- Release Plone 5.2.4 final.
  No changes compared to last release candidate.
  [maurits] (#3250)


5.2.4rc2 (2021-03-02)
---------------------

Bug fixes:


- Fixed tests in combination with Products.PluggableAuthService 2.6.0.
  [maurits] (#3251)


5.2.4rc1 (2021-02-19)
---------------------

Bug fixes:


- Bumped metadata version to 5211.
  [maurits] (#5211)


5.2.3 (2020-11-19)
------------------

Bug fixes:


- Release Plone 5.2.3 final.
  No changes compared to last release candidate.
  [maurits] (#3199)


5.2.3.rc1 (2020-10-30)
----------------------

Bug fixes:


- No longer doubly undo a response Content-Type change when combining bundles.
  [maurits] (#1924)
- Fix issue with @@search view when filtering by creation date
  [frapell] (#3007)
- Fixed use of own ``utils.isDefaultPage``, which should be ``defaultpage.check_default_page_via_view``.
  [maurits] (#3130)
- Fixed invalid escape sequences in regular expressions.
  [maurits] (#3130)
- Fixed deprecation warning for zope.site.hooks.
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
- Robot tests: Do not use jQuery.size() but use ``.length`` instead.
  ``.size()`` is deprecated since 1.8.
  [thet] (#3195)


5.2.2 (2020-08-16)
------------------

Bug fixes:


- Release Plone 5.2.2 final.
  No changes with last release candidate, except that the versions will contain Products.isurlinportal 1.1.0 with a minor security hardening fix.
  [maurits] (#3510)


5.2.2rc3 (2020-08-16)
---------------------

Bug fixes:


- Return a Zope aware engine for page templates based on ``zope.pagetemplate`` instead of ``Products.PageTemplates``.
  Fixes possible problems with such templates, for example z3c.form ones, with Zope 4.4 and higher.
  See `issue 3141 <https://github.com/plone/Products.CMFPlone/issues/3141>`_.
  [maurits] (#3141)
- Depend on new package ``Products.isurlinportal``.
  This contains the ``isURLInPortal`` method that was split off from our ``URLTool``.
  See `issue 3150 <https://github.com/plone/Products.CMFPlone/issues/3150>`_.
  [maurits] (#3150)
- Redirection view: refactor our navigation root editing to a separate method ``edit_for_navigation_root``.
  Since Plone 5.2 the redirectiontool respects INavigationroot:
  with a manual redirect you cannot enter a path starting with ``/`` which 'escapes' the NavigationRoot to the SiteRoot to link to another part of the Plone instance.
  This refactor makes it possible to override this method to return the redirection unchanged, brining back the pre Plone 5.2 behavior of the ``Products.RedirectionTool`` add-on.
  [maurits] (#3153)
- Control panel configlets: first check visibility, then check condition.
  Visibility is cheaper to check.
  Also fixes `bug 3154 <https://github.com/plone/Products.CMFPlone/issues/3154>`_.
  [maurits] (#3154)


5.2.2rc2 (2020-07-17)
---------------------

Bug fixes:


- Fix an issue in mail_password_template.pt in the message showing the ip to really try the request.REMOTE_ADDR variable if request.HTTP_X_FORWARDED_FOR is empty (when you're not behind apache or nginx).
  [vincentfretin] (#2949)
- mail_password form: Do not crash if the userid is not provided or the user doesn't have an email configured
  [frapell] (#3008)


5.2.2rc1 (2020-06-28)
---------------------

New features:


- Image caption support
  Allow ``figcaption`` in rich text editor as a valid tag.
  Add registry setting for plone.image_caption outputfilter transform.
  [thet] (#2887)
- Add markdown extension settings to markup control panel.
  [thomasmassmann] (#3076)
- Insert virtual custom.css bundle into the header after diazo bundle.
  Only add this when custom css is set in the theming control panel.
  [MrTango] (#3086)


Bug fixes:


- Change control panel item sorting and sort them by title
  [erral] (#721)
- Update HTMLFilter settings to enable TinyMCE styling features. See #2329, #2482, #2535
  [petschki] (#2482)
- If 'tinymce-content-css' option is missing in themes manifest.cfg prevent unnecessary loading of a css at nav_root_url while editing a page.  [krissik] (#2861)
- Redirect (when possible) also ajax requests and do not return an unuseful body
  [ale-rt] (#3014)
- Merge Hotfix20200121 Check of the strength of password could be skipped. (#3021)
- Merge Hotfix20200121: isURLInPortal could be tricked into accepting malicious links. (#3021)
- Improve tests for the workflow tool method listWFStatesByTitle (#3032)
- Fix index_html on PortalRoot: ReplaceableWrapper did not work.
  [jensens] (#3060)
- Allow accessing ``plone_view.patterns_settings``.
  This was no problem until now, but a newer ``Zope/zope.tales/Chameleon``  is rightly stricter.
  [maurits] (#3066)
- Fix Python 3.8 ``time.clock`` removal in CatalogTool [jensens] (#3082)
- Fixed TypeError when adding both a group and a user to a group.
  [maurits] (#3084)
- Make the resource registry scripts output more robust when a bundle resource is missing. This prevents
  breaking your whole Plone site and access to the resource registry control panel after inserting
  one missing resource. 
  [fredvd] (#3096)
- Bugfix for #3103
  [petschki] (#3105)
- Fixed saving ignored exception types in Python 3.  [maurits] (#3115)


5.2.1 (2020-01-13)
------------------

New features:


- Add plone.staticresources to list of addons which are automatically upgraded if upgrade steps are available.
  [thet] (#2976)


Bug fixes:


- fix creation of Plone site not adding default Dexterity content types if example content not explicitily selected by user.
  [ericof] (#1318)
- fix default value for email msgid
  [erral] (#2790)
- Fix: PasswordResetView::getErrors is called, this ensures password is validated through RegistrationTool before attempting to reset password.
  [nazrulword] (#2917)
- Breadcrumbs: consider hidden folders when creating urls [ksuess] (#2935)
- Add Collection to the default_page_types list
  [erral] (#2956)
- Fix localization of "Site setup" in some control panels [vincentfretin] (#2958)
- Fix TTW Bundle compilation broken.
  [thet] (#2969)
- Do not save type settings in "content-controlpanel" when switching between types.
  [cekk] (#2986)
- Correctly fire events when user autologin after the password has been reset.
  [ericof] (#2993)


5.2.0 (2019-07-10)
------------------

Bug fixes:


- Don't activate all sorting tabs when no sort option has been chosen.
  [gyst, rodfersou, jensens] (#1789)
- Fix test failures exposed in Python 3.8
  [pbauer] (#2903)


5.2rc5 (2019-06-27)
-------------------

New features:


- Add support for Python 3.8 [pbauer] (#2896)


Bug fixes:


- Add missing i18n:translate calls
  [erral] (#2891)
- Fix login-help layout on mobile.
  [jensens] (#2893)


5.2rc4 (2019-06-20)
-------------------

New features:


- Remove verifydb, it was moved to standalone package zodbverify.
  [jensens] (#2858)


Bug fixes:


- If specified in the registry, let the user autologin after the password has been reset (#2439)
- Allow empty ``default_page`` registry setting
  [petschki] (#2813)
- Always add ``data-default-sort`` attribute to search results.  [maurits] (#2854)
- Fix deprecation warnings.
  [jensens] (#2862)
- Use the shared 'Plone test setup' and 'Plone test teardown' keywords in Robot tests.
  [Rotonen] (#2864)
- Fix script resource parsing error because of self closing tags.
  [Netroxen] (#2870)


5.2rc3 (2019-05-04)
-------------------

New features:


- Allow filtering on date and manual/automatic in redirection controlpanel. (#2799)
- Add a button to export the alternative urls in redirection controlpanel. (#2799)
- Add a button to remove all alternative urls that match the filter.
  See `issue 2799 <https://github.com/plone/Products.CMFPlone/issues/2799>`_.
  [maurits] (#2799)


Bug fixes:


- gracefully handle tracebacks during addon installation
  [petschki] (#2228)
- Add workaround for the case when a inifite recusion in a page-template that uses the main-template crashes the instance instead of raising a RecursionError.
  [pbauer, esteele] (#2666)
- Fixed unstable Markup Control Panel robot test again.  [maurits] (#2809)
- add a missing space in an error message in the redirects control panel and replace "deffered" by "deferred" [vincentfretin] (#2821)
- Fixes: Cooking resources with non ASCII resulted in encoding error.
  Further, writing legacy resources resulted in ValueError. [jensens] (#2827)
- restore ``exclude_from_nav`` combined with ``show_excluded_items`` handling
  [petschki] (#2828)
- Fix DeprecationWarning in syndication-view. [jensens] (#2831)
- Fix malformed url when redirecting to external login. [ericof] (#2842)
- Make navigation (CatalogNavigationTabs) subclassing easier. [iham] (#2849)


5.2rc2 (2019-03-21)
-------------------

Bug fixes:


- Fix excluded items in navigation [ale-rt] (#2516)
- Add basic validators for the portal action controlpanel forms (#2689)
- Fix wrong msgids in link management control panel [erral] (#2788)
- Fix errors that abort the verification when debugging a DB with ./bin/instance verifydb -D.
  [pbauer] (#2792)
- Add summary of all errors when verifying a DB with ./bin/instance verifydb.
  [pbauer] (#2798)
- Fixed unstable SearchableText and Scenario Type querystring robot tests.  [maurits] (#2808)
- Fixed unstable Markup Control Panel and other robot tests.   [maurits] (#2809)


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
- Make linkintegrity robot test more reliable [MrTango] (#2752)
- Check only once if Products.ATContentTypes is available. [gforcada] (#2765)
- Fix redirection to `came_from` when url matches LOGIN_TEMPLATE_ID partly
  [petschki] (#2771)


5.2b1 (2019-02-13)
------------------

Breaking changes:


- Factor out all static resources and the ``plone-compile-resources`` script
  into plone.staticresources. [thet] (#2542)


New features:


- PLIP 1486: Merge Products.RedirectionTool into core. Allow users to manage
  redirects on their site and aliases to content. See
  https://github.com/plone/Products.CMFPlone/issues/1486 [staeff, maurits]
  (#1486)
- Added multilevel dropdown navigation [agitator] (#2516)
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
