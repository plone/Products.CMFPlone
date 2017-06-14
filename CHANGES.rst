.. This file should contain the changes for the last release only, which
   will be included on the package's page on pypi. All older entries are
   kept in HISTORY.txt

Changelog
=========


5.0.9 (unreleased)
------------------

Breaking changes:

- *add item here*

New features:

- Include JS Patterns when loading a page via ajax or an iframe
  [displacedaussie, instification]

Bug fixes:

- *add item here*


5.0.8 (2017-06-04)
------------------

Bug fixes:

- Fix default value for ``robots.txt`` to avoid issues with content containing "search" in the id.
  [hvelarde]

- Show version of products in Add-ons control panel configlet.
  This fixes https://github.com/plone/Products.CMFPlone/issues/1472.
  [hvelarde]

- Removed "change portal events" permission
  [kakshay21]

5.0.7 (2017-02-20)
------------------

New features:

- Added ``ok`` view.  This is useful for automated checks, for example
  httpok, to see if the site is still available.  It returns the text
  ``OK`` and sets headers to avoid caching.
  [maurits]

- Include a new release of mockup.
  [thet]

- Move ``get_top_site_from_url`` from plone.app.content to ``utils.py``.
  This function allows in virtual hosting environments to acquire the top most visible portal object to operate on.
  It is used for example to calculate the correct virtual root objects for Mockup's related items and structure pattern.
  [thet]

Bug fixes:

- Fix wrong TinyMCE configuration for multilingual sites [erral]

- Added security checks for ``str.format``.  Part of PloneHotfix20170117.  [maurits]

- Load some patches earlier, instead of in our initialize method.  [maurits]

- Fixed workflow tests for new ``comment_one_state_workflow``.  [maurits]

- Fixed sometimes failing search order tests.  [maurits]

- Load some Products.CMFPlone.patches earlier, instead of in our initialize method.
  This is part of PloneHotfix20161129.
  [maurits]

- Fix Search RSS link condition to use search_rss_enabled option and use
  rss.png instead of rss.gif that doesn't exist anymore.
  [vincentfretin]

- Fix potential KeyError: admin in doSearch in Users/Groups controlpanel.
  [vincentfretin]

- Prevent workflow menu overflowing in toolbar [MatthewWilkes]

- Add default icon for top-level contentview and contentmenu toolbar entries [alecm]

- Fix various layout issues in toolbar [alecm]

- Fix TinyMCE table styles [vangheem]

- Apply security hotfix 20160830 for ``z3c.form`` widgets.  [maurits]

- Fixed tests in combination with newer CMFFormController which has the hotfix.  [maurits]

- Apply security hotfix 20160830 for ``@@plone-root-login``.  [maurits]

- Apply security hotfix 20160830 for ``isURLInPortal``.  [maurits]

- Bundle aggregation must use ++plone++static overrided versions if any.
  [ebrehault]

- Fix bundle aggregation when bundle has no CSS (or no JS)
  [ebrehault]

- Fix relative url in CSS in bundle aggregation
  [ebrehault]

- Don't fail, when combining bundles and the target resource files (``BUNLDE-compiled.[min.js|css]``) do not yet exist on the filesystem.
  Fixes GenericSetup failing silently on import with when a to-be-compiled bundle which exists only as registry entry is processed in the ``combine-bundle`` step.
  [thet]

- Don't fail, if ``timestamp.txt`` was deleted from the resource registries production folder.
  [thet]

- Fix security test assertion:
  TestAttackVectorsFunctional test_widget_traversal_2 assumed a 302 http return code when accessing some private API.
  Meanwhile it changed to return a 404 on the URL.
  Reflect this in the test and expect a 404.
  [jensens]

- Fix atom.xml feed not paying attention for setting to show about information
  [vangheem]

- Do not encode reply-to email address for contact-info form
  [tkimnguyen]

5.0.6 (2016-09-23)
------------------

Bug fixes:

- Have more patience in the thememapper robot test.  [maurits]

- Fixed adding same resource/bundle to the request multiple times. [vangheem]

- Fixed missing keyword in robot tests due to wrong documentation lines.  [maurits]

- Marked two robot tests as unstable, non-critical.
  Refs https://github.com/plone/Products.CMFPlone/issues/1656  [maurits]

- Use ``Plone Test Setup`` and ``Plone Test Teardown`` from ``plone.app.robotframework`` master.  [maurits]

- Fix select2 related robot test failures and give the test_tinymce.robot scenario a more unique name.
  [thet]

- Updated TinyMCE to fix a bug caused by a jQuery conflict that prevented controls working on some Chrome borwser.
  [MatthewWilkes]


5.0.5c2 (2016-06-22)
--------------------

New features:

- Supported ``remove`` keyword for configlets in controlpanel.xml.  [maurits]

- Fixed displaying the body text of a feed item.  This is when
  ``render_body`` is switched on in the Syndication settings.
  [maurits]

- Removed docstrings from some methods to avoid publishing them.  From
  Products.PloneHotfix20160419.  [maurits]

- Ensured front-page is English when creating an English site.
  Previously, when creating an English site with a browser that
  prefers a different language, the body text ended up being in the
  browser language.  For languages without a front-page text
  translation the same happened: they got the other language instead
  of English.  [maurits]

- Bundle aggregation must use ++plone++static overrided versions if any.
  [ebrehault]

- Fix bundle aggregation when bundle has no CSS (or no JS)
  [ebrehault]

- Do not hard-code baseUrl in bundle to avoid bad URL when switching domains.
  [ebrehault]

Bug fixes:

- Removed docstrings from PropertyManager methods to avoid publishing them.  [maurits]

- Added publishing patch from Products.PloneHotfix20160419.
  This avoids publishing some methods inherited from Zope or CMF.  [maurits]

- Fix issue where incorrectly configured formats would cause TinyMCE to error
  [vangheem]



5.0.4 (2016-04-06)
------------------

Fixes:

- Bump profile version.
  [esteele]


5.0.3.1 (2016-03-29)
--------------------

Fixes:

- In the ``combine-bundles`` import step, make sure the Content Type
  header is not set to ``application/javascript``.  This would result
  in the ``plone-upgrade`` result page being shown in plain text.
  Fixes https://github.com/plone/Products.CMFPlone/issues/1436
  [maurits]


5.0.3 (2016-03-16)
------------------


New:

- Upgrade TinyMCE to 4.3.4
  [vangheem]

- If a bundle does not provide any resources, do not attempt to compile it
  [vangheem]

- Build resource registry JavaScript for fix in not being able to develop js/css
  [vangheem]

- Include pat-moment for public javascript
  [vangheem]

- Add custom navigation root in TinyMCE configuration.
  [alecm]

- Add barceloneta theme path in less configuration.
  [Gagaro]

- Merge JS and CSS bundles into meta-bundles to reduce the number of requests
  when loading a page (PLIP #1277)
  [ebrehault]

Fixes:

- Fix browser spell checking not working with TinyMCE
  [vangheem]

- Do not fail when viewing any page, or during migration, when Diazo
  is not installed and the persistent resource directory is not
  registered.  Fixes
  https://github.com/plone/Products.CMFPlone/issues/1187
  [maurits]

- Move hero on welcome page from theme into managed content.
  Issue https://github.com/plone/Products.CMFPlone/issues/974
  [gyst]

- Get ``email_from_name`` from the mail settings registry.
  Fixes https://github.com/plone/Products.CMFPlone/issues/1382
  [tmog]

- No longer rely on deprecated ``bobobase_modification_time`` from
  ``Persistence.Persistent``.
  [thet]

- Move p.a.discussion monkey patch for reindexing conversations to
  CatalogTool.py as p.a.discussion is part of Plone core.
  Issue https://github.com/plone/Products.CMFPlone/issues/1332
  [fredvd, staeff]

- Fix custom tinymce content styles not getting included correctly
  [vangheem]

- Fix timing problem with robot framework tests.
  [jensens]

- Upgrade TinyMCE to 4.3
  [vangheem]

- Fix use of icons in search results
  [vangheem]

- Mock MailHost on testing.py so that tests relying on mails can use it.
  [gforcada]

- Fix `aria-hidden` attribute control problem on toolbar
  https://github.com/plone/Products.CMFPlone/issues/866
  [terapyon]

- Sort relateditems tree by sortable_title in tinymce.
  [Gagaro]

- Return a JSON error instead of a the Plone error page when the requested
  resource is not text/html (fix #637).
  [ebrehault]


5.0.2 (2016-01-08)
------------------

Fixes:

- Fix url generation for tinymce when using virtual hosting. This fixing
  images not rendering properly in tinymce.
  [vangheem]

- build resources with latest mockup that provides better path criteria
  widget for the querystring pattern
  [vangheem]

- Fixed Forbidden error when using the users and groups overview as
  Site Administrator.  This could happen when there are users that
  inherit the Manager role from the Administrators group.
  Fixes issue https://github.com/plone/Products.CMFPlone/issues/1293
  [maurits]

- Fixed Unauthorized error in folder_full_view for anonymous users.
  Fixes issue https://github.com/plone/Products.CMFPlone/issues/1292
  [maurits]


5.0.1 (2015-12-17)
------------------

New:

- Add option to show/hide thumbs in site-controlpanel
  https://github.com/plone/Products.CMFPlone/issues/1241
  [fgrcon]

- Add icon fallback for addons in Site Setup (fixes `#1232`_)
  [davilima6]

- Explicitly provide id on search form and not depend on diazo magic
  adding the id in.
  [vangheem]

- Be able to stub JavaScript modules to prevent including the same
  javascript twice.
  [vangheem]

- Set Reply-to address in contact-info emails so you can reply to them.
  [tkimnguyen, maurits, davisagli]

- Added syndication for plone.app.contenttypes collections.
  [do3cc]

- Compress generated bundle CSS file when running ``plone-compile-resource``.
  [petschki]

- Added new commandline argument to plone-compile-resource: ``--compile-dir``.
  [petschki]

- Upgraded to patternslib 2.0.11.
  [vangheem]

- Allowed all TinyMCE settings to be set from control panel.
  [Gagaro]

- Added missing_value parameter to controlpanel list and tuple fields.
  [tomgross]

- Split hard coded JavaScript resources into seperate method for easier
  customization.
  [tomgross]

Fixes:

- Fix internal links and images src to not include the domain.
  [Gagaro]

- Update Site Setup link in all control panels (fixes `#1255`_)
  [davilima6]

- In tests, use ``selection.any`` in querystrings.  And expect this in
  the default news and events collections.
  Issue https://github.com/plone/Products.CMFPlone/issues/1040
  [maurits]

- Add authenticator token to group portlet links
  [vangheem]

- Fix bbb global status message template rendering escaped html
  [vangheem]

- Avoid AttributeError if registry is not yet there for the
  JSRegistryNodeAdapter while migrating from older versions
  https://github.com/plone/Products.CMFPlone/pull/1246
  [frapell]

- remove deprecated icons ...
  https://github.com/plone/Products.CMFPlone/issues/1226
  [fgrcon]

- Also remove deprecated icons for archetypes
  [Gagaro]

- Fixed white space pep8 warnings.
  [maurits]

- Prevented breaking Plone when TinyMCE JSON settings fields contain
  invalid JSON.
  [petschki]

- Fixed #1199: prevent throwing error with mis-configured bundle.
  [vangheem]

- Fixed wrong sentence in front page.  There is no "Site Setup entry
  in the menu in the top right corner".  Replaced it by "Site Setup
  entry in the user menu".
  [vincentfretin]

- Fixed some i18n issues.
  [vincentfretin]

- Used unique traverser for stable resources to set proper cache headers.
  [alecm]

- Fixed "contains object" tinymce setting not getting passed into pattern
  correctly.  Fixes #1023.
  [vangheem]

- Fixed issue when csscompilation and/or jscompilation are missing in
  bundle registry record.
  [peschki]

- Fixed #1131: Allow to compile bundle with more than one resource.
  [timitos]

- Fixed issue where clicking tabs would cause odd scroll movement.
  [vangheem]

- When migration fails, do not upgrade addons or recatalog or update
  roles.
  [maurits]

- Default values for interfaces.controlpanel.IImagingSchema.allowed_sizes
  should be unicode.
  [kuetrzi]

- Don't depend on and install plone.app.widgets. plone.app.z3cform does it for
  us.
  [thet]


5.0 (2015-09-27)
----------------

- Update hero text. Remove "rocks" line, more descriptive link button.
  [esteele]

- Be able to provide table styles in tinymce configuration
  [vangheem]

- Fix #1071: AttributeError when saving theme settings
- Remove unused types_link_to_folder_contents setting
  [vangheem]

- Fix #817: When saving the filter control panel show a flash message with
  info on caching.
  [jcerjak]

- Remove Chrome Frame from ``X-UA-Compatible`` HTTP header as it's deprecated.
  [hvelarde]

- Fix mail controlpanel not keeping password field when saving
  [allusa]

- Remove trying to install plone.protect to global site manager
  as that is now handled by plone.protect
  [vangheem]

- Fix traceback style (closes `#1053`_).
  [rodfersou]

- Let plone-final import step also depend on the workflow step.
  Otherwise the plone-final step installs plone.app.discussion with an
  extra workflow, and then our own workflow step throws it away again.
  Closes `#1041`_.
  [maurits]

- Purge profile upgrade versions from portal_setup when applying our
  default CMFPlone:plone profile.  This signals that nothing has been
  installed yet, so depencies will get reapplied instead of possibly
  upgraded.  This could cause problems mostly in tests.  Closes
  `#1041`_.
  [maurits]

- Fix image preview in TinyMCE editor when in modals.
  [Gagaro]


5.0rc3 (2015-09-21)
-------------------

- Fix i18n in accessibility-info.pt
  [vincentfretin]

- Resolve deprecation warnings about portal_url
  [fulv]

- Improve contrast for pending state when state menu active (closes `#913`_).
  [rodfersou]

- Fix buttons positions on resource registry (closes `#886`_).
  [rodfersou]

- Add missing file for ace-editor to edit XML files (closes `#895`_).
  [rodfersou]

- Remove empty options for Site Settings configlet (closes `#996`_).
  [rodfersou]

- Hide document byline viewlet by default.
  [esteele]

- Move portal property email_charset to the registry.
  [esteele]

- Fix `#950`_: Missing personal toolbar when expanding the horizontal toolbar
  [ichim-david]

- Make sure portal_actions are imported before default portlets.
  Fixes `#1015`_.
  [vangheem]

- Move calendar_starting_year and calendar_future_years_available to
  registry and Products.Archetypes.
  [pbauer]

- Use registry lookup for types_use_view_action_in_listings
  [esteele]

- Add view @@hero to be included by plonetheme.barceloneta with diazo.
  [pbauer]

- Fix `#991`_: improve contrast for pending state in tollbar.
  [pabo3000]

- remove unused code to create NavTree probably left from Plone 3.0 times
  and since a while handled by plone.app.portlets.

- add navigation root registry value
  [jensens]

- Implement new feed syndication using `NewsML 1 <http://iptc.org/standards/newsml-1/>`_,
  an IPTC standard that provides a media-type-independent, structural framework for multi-media news.
  [frapell, jpgimenez, tcurvelo, rodfersou]

- provide positive number validator
  [vangheem]

- Move external_links_open_new_window, redirect_links to the registry.
  [esteele]

- Remove invalid_ids portal property as it isn't used.
  [esteele]

- Fix `#963`_: respect icon visibility setting
  [vangheem]

- Fix `#935`_: Fix group membership form rendering when group can't be found.
  [esteele]

- Fix redirect for syndication-controlpanel.
  [pbauer]

- Add advanced-option to button "Add Plone Site" in ZMI.
  [pbauer]

- Fix `#952`_: Toolbar menu completely misplaced because of link duplication
  [ichim-david]

- Fix issue where some filter settings would not get saved and provide
  correct defaults
  [vangheem]

- Better default tinymce settings
  [vangheem]

- Give some padding at the bottom of the toolbar menu dropdowns
  [sneridagh]

5.0rc2 (2015-09-11)
-------------------

- Move login properties to the configuration registry.
  [esteele]

- Fix changing searchable in types-controlpanel.
  Fix `#926`_.
  [pbauer]

- Respect view-url in livesearch-results. Fixes `#918`_.
  [pbauer]

- Fix Livesearch for items without review_state (files and image). Fixes #915.
  [pbauer]

- Apply isURLInPortal fix from https://pypi.python.org/pypi/Products.PloneHotfix20150910
  [vangheem]

- Do not bother additional CRSF protection for addMember since all public
  users get same CSRF token and the method should be unpublished.
  See https://pypi.python.org/pypi/Products.PloneHotfix20150910
  [vangheem]

- Remove site properties that have been migrated to the registry.
  [esteele]

- fix `#862`_: Profile listing on site creation has alignment issues
  [ichim-david]


5.0rc1 (2015-09-08)
-------------------

- Remove deprecated global_defines.pt
  [esteele]

- Remove no-longer-used properties from portal_properties
  [esteele]

- Move footer and colophon out of skins
  [vangheem]

- pre-cook resources so we do not write on read for resources generation
  [vangheem]

- Turn robots.txt into a browser-view, fix link to sitemap.xml.gz, allow
  editing in site-controlpanel.
  Fixes `#604`_.
  [pbauer]

- Remove history_form, history_comparison templates.
  Remove now-empty plone_forms skins folder.
  [esteele]

- Remove no-longer-used images from portal_images.
  [esteele]

- Typo in delete modal configuration caused submission redirection errors
  [vangheem]

- Upgrade known core packages at the end of the Plone migration.
  [maurits]

- remove Products.CMFPlone.utils.isLinked function. Switch to using
  plone.app.linkintegrity's variant
  [vangheem]

- Fix error to allow site navigation if TinyMCE content_css setting is None
  [Gagaro]

5.0b4 (2015-08-23)
------------------

- fix `#350`_: "plone.app.content circular dependency on Products.CMFPlone" - this
  fixes the imports only, not on zcml/genericsetup level.
  [jensens]

- move Plone specific ``getDefaultPage`` (magic) code from plone.app.layout
  over to Products.CMFPlone. This avoids a circular dependency. Also its
  not really layout only related code.
  [jensens]

- Fix add-ons to be installed using CMFQuickInstaller (restore support
  for Extensions/Install.py)
  [datakurre]

- Rename showEditableBorder to showToolbar and deprecate using
  disable_border and enable_border for enable_toolbar and disable_toolbar
  [vangheem]

- Not using less variables in toolbar everywhere
  [vangheem]

- Fix link to documentation

- Rework timezone selection in @@plone-addsite.
  [jaroel]

- Rework language selection in @@plone-addsite.
  [jaroel]

- Turn @@tinymce-controlpanel ``content_css`` field into a list, so we can add
  several CSS URLs (useful when add-ons need to provide extra TinyMCE styles),
  and fix TinyMCE config getter so it considers the ``content_css`` value.
  [ebrehault]


5.0b3 (2015-07-20)
------------------

- show toolbar buttons on sitemap, accessibility and search pages
  [vangheem]

- log info after catalog rebuilt
  [vangheem]

- Renamed 'Zope Management Interface' to 'Management Interface'.
  [jaroel, aclark]

- Fix adding a new Plone site with country specific language. Refs `#411`_.
  [jaroel]

- fix plone-logged-in bundle not using global jquery for requirejs dependency and in
  weird cases causing select2 load errors in patterns(especially resource registry)
  [vangheem]

- Use new plone.app.theming policy API and delegate theme cache to plone.app.theming
  [gyst]

- Fix issue where site root syndication was giving 404s
  [vangheem]

- update time widget interval selection to be the same as Plone 4 time selection intervals
  [vangheem]

- use ajax_load in @@search when loading results dynamically, and add missing
  closing tag
  [ebrehault]

- better formatting of config.js
  [vangheem]

- Upload pattern uses the baseUrl to compute the upload URL, so this should
  always be the site root and not the current context
  [frapell]

- rewrite css files when saving customized files in the resource registry
  [vangheem]

- Update links to point to '@@overview-controlpanel'.
  Fixes `#573`_.
  [gforcada]

- Fix email validation of long domain names.
  [gotcha]

- fix syndication feed use of lead image as it was using wrong url
  [vangheem]

- add utility to get site logo
  [vangheem]

- fix issue where product upgrade did show an error status message
  [datakurre]

- fix casing on "First weekday" field on Date and Time control panel
  [vangheem]

- fix imaging control panel example format on description
  [vangheem]

- Add page title to resource registry
  [vangheem]

- Remove ramcache-controlpanel csrf test. Ramcache control panel has been
  moved to p.a.caching since ages. We will get rid of it.
  [timo]

- Add undeclared zope.cachedescriptors dependency.
  [timo]

- Do not require "Enable LiveSearch". This fixes `#558`_.
  [timo]

- Fix control panel titles. This fixes `#550`_, `#553`_, `#557`_.
  [timo]

- remove plone.app.jquerytools dependency
  [vangheem]

- fix bug where bundles would not get built properly with
  compile-plone-resources script when multiple resources
  were defined for a bundle
  [vangheem]

- do not require css to be defined for non-compilable bundles
  [vangheem]

- fix weird issue with selecting multiple links and images on a page
  while you are editing with tinymce
  [vangheem]

- updates to contact forms to make them more user friendly on submission
  [vangheem]

- include code plugin by default for TinyMCE
  [vangheem]

- Fix build reading browser cached files by appending random query
  param onto url. See `commit 2d3865805efc6b72dce236eb68e502d8c57717b6`_
  and `commit bd1f9ba99d1ad40bb7fe1c00eaa32b8884aae5e2`_.
  [vangheem]

- fix manage content type and group portlets link to have authenticator
  [vangheem]

- Convert manage-portlets.js into a pattern and make improvements on
  using the manage portlets infrastructure
  [vangheem]

- Remove dependency on plone.app.form and other formlib packages
  [tomgross]

- Remove plone.skip_links from the default set of viewlets in order to follow
  modern a11y methods and drop support for outdated ways [sneridagh]

- Change the name and link of 'Types' control panel to 'Content Settings' and
  '@@content-controlpanel' since there was confusion with the 'Dexterity
  Content Types' one [sneridagh]


5.0b2 (2015-05-13)
------------------

- Add social media settings control panel

- add ability to provide a css file for tinymce style formats
  [vangheem]

- fix plone-generate-gruntfile to compile each less resource
  separately
  [vangheem]

- provide image alignment styles for tinymce images
  [vangheem]

- Respect TinyMCE control panel settings
  [vangheem]

- enable/disable versioning behavior with settings in Types control panel
  [vangheem]

- Make ``typesToList`` read ``metaTypesNotToList`` from new p.a.registry settings.
  This fixes `#454`_.
  [timo]

- style tweaks to toolbar
  [pbauer]

- fix search form usability
  [vangheem]

- detect when changes are made to the legacy bundle through the interface
  so resources are re-built when they need to be
  [vangheem]

- fix some legacy import wonkiness. Inserting multiple times, insert-before
  and remove fixed
  [vangheem]

- make live search and search form give consistent results
  [vangheem]

- only show edit bar if user logged in
  [vangheem]

- fix error sending test email in Mail control panel
  [tkimnguyen]

- pat-modal pattern has been renamed to pat-plone-modal
  [jcbrand]

- Remove Products.CMFFormController dependency.
  [timo]

- Fix submission of tinymce control panel.
  [davisagli]

- Monkey patch SMTPMailer init method to pick up the mail settings from the
  registry instead of from the MailHost itself.
  [timo]

- Add `resource_blacklist` attribute to resource registry importer, to
  allow filtering of known bad legacy resource imports.  Filter js from
  plone.app.jquery.
  [alecm]

- Fix broken "Installing a third party add-on" link
  [cedricmessiant]

- Fix folder contents button disappeared act
  [vangheem]

- Fix resource registry javascript build
  [vangheem]

- Move `plone.htmlhead.links` viewlet manager after `plone.scripts`,
  because the former is sometimes used to include scripts that depend on
  the latter.
  [davisagli]

- Change the order of the plonebar user menu and move the plone.personal_bar
  viewlet to the last position due to accessibility issues on having it being
  the first element.
  [sneridagh]

- We only support `utf-8` site-encoding at the moment
  [tomgross]


5.0b1.post1 (2015-03-27)
------------------------

- Packaging fix, no code changes.
  [esteele]


5.0b1 (2015-03-26)
------------------

- Add tests for configuring encoding of user registration or
  forgotten password emails.
  [davidjb]

- Pass email encoding to forgotten password email template.
  [davidjb]

- Pass mail ``Content-Type`` to mailhost when sending forgotten password
  emails.
  [davidjb]

- Move security control panel to CMFPlone. Fixes `#216`_.
  [jcerjak, timo]

- Remove ``create_userfolder`` from addPloneSite factory, it is not used
  anymore.
  [jcerjak]

- Read security settings from the registry instead of portal properties.
  [jcerjak,timo]

- Fix tests for plone.app.contenttypes unified view names, which uses
  ``listing_view`` for Folder and Collection types.
  [thet]

- Remove ``selectable_views`` from ``properties.xml``, which isn't used
  anywhere anymore.
  [thet]

- Remove the remaining ``Topic`` entry in ``default_page_types`` from
  ``propertiestool.xml``. This setting is now done in
  ``plone.app.contenttypes`` respectively ``Products.ATContentTypes``.
  [thet]

- Add __version__ attribute to __init__.py. This allows us to retrieve the
  current Plone version with 'Products.CMFPlone.__version__'. Even though this
  is no offical standard, many packages in the Python standard library provide
  this.
  [timo]

- Replaced the legacy mark_special_links javascript with a
  corresponding mockup pattern.
  [fulv]

- remove plone_javascript_variables.js as necessary values
  are provided on body tag and pattern options
  [vangheem]

- fix bootstrap css bleeding into global namespaces
  [vangheem]

- add recurrence pattern
  [vangheem]

- add history support for folder contents
  [vangheem]

- Merge plone.app.search here
  [vangheem]

- Extended ulocalized_time for target_language
  [agitator]

- Caching for ``@@site-logo``.
  [thet]

- Support for portal site logos stored in the portal registry by uploading via
  the site control panel. Add a ``@@site-logo`` view for downloading the logo.
  [thet]

- Fix the resource registry to save the automatically generated filepath to the
  compiled resource on the bundle object after compilation. The filepath is
  always in the '++plone++static/' namespace. This fix makes custom bundles
  actually includable.
  [thet]

- Get icon from layout_view instead of plone_view.
  [pbauer]

- Fix contentViews (tabs) markup for Plone 5.
  [davisagli]

- Rename syndication-settings to syndication-controlpanel. Keep the old view registration for backwards compatibility.
  [timo]

- Added a link for the advanced 'Create a Plone site' screen to the Plone overview.
  [jaroel]

- Fixed the label for 'Example content' in the advanced 'Create a Plone site' screen.
  [jaroel]

- Move markup control panel to CMFPlone. Fixes `#220`_.
  [djay, thet]

- Use jstz to set default portal_timezone in @@plone-addsite.
  [instification]

- Make inline validation of AT multiple selection widget work.
  [gbastien]

- Make sure compiling resources does not commit transaction prematurely.
  [davisagli]

- Adding the option to configure a bundle from the diazo manifest file.
  [bloodbare]

- Move the controlpanel overview from plone.app.controlpanel into this package
  Fixes `#290`_.
  [khink]

- PLIP 10359: Migrate usergroups controlpanel to ``z3c.form`` and move it from
  plone.app.controlpanel to Products.CMFPlone. Fix and extend tests and add
  robot tests.
  [ferewuz]


5.0a3 (2014-11-01)
------------------

- folder_position script: make position and id optional.  Default
  position to 'ordered' and id to None, which means: do nothing.
  plone.folder 1.0.5 allows this, making it possible to simply reverse
  the current sort order by using reverse=False.
  [maurits]

- Fix JS resource viewlet HTML syntax error.
  [rpatterson]

- Fix resource bundle expressions.  They weren't being checked at all and
  reversed the condition if they had been.  Also move caching of the cooked
  expressions out of the DB and into a RAM cache.
  [rpatterson]

- Fix endless resource dependency loop when dependeing on a bundle that also has
  a dependency.
  [rpatterson]

- reduce deprecation warnings to use plone_layout and not plone_view for
  certain method calls in order to make debugging of robottests easier:
  w/o it shows 1000ds of extra lines in html report.
  [jensens]

- type controlpanel: Resolved problem with workflow selection form as it
  was breaking if state title had non-ascii characters. see also
  https://github.com/plone/plone.app.controlpanel/pull/26
  [lewicki, jensens]

- Minor overhaul of CatalogTool.py - no feature changes!
  Optimizations and better readable code for indexer
  ``allowedRolesAndUsers``: now using a set.
  Change if/elif/else to oneliner boolean expression in ``is_folderish``
  indexer.
  Usage of AccessControl 3 style decorators for security declarations.
  Minor reformattings to make code-analysis happy.
  [jensens]

- Removed some javascripts: fullscreenmode.js, dragdropreorder.js,
  styleswitcher.js, select_all.js, collapsibleformfields.js

- PLIP 13260: Migration cut, copy and paste into browser views.
  [saily]

- Abstract the search form and livesearch action URLs making it easier to
  extend the search portlet with custom views or other actions.
  [rpatterson]

- Fix JavaScript to work with recent jQuery (>= 1.9) versions.
  [thet]

- Small scoping fix in locking js code
  [do3cc]

- PLIP 13260: Migrate author page to browser views/z3c.form (issue `#78`_)
  [bosim]

- Integration of the new markup update and CSS for both Plone and Barceloneta
  theme. This is the work done in the GSOC Barceloneta theme project.
  [albertcasado, sneridagh]

- Created new viewlet manager for holding main navigation for a more semantic
  use of it. Move the global sections viewlet into it.
  [albertcasado]

- New toolbar markup based in ul li tags.
  [albertcasado, bloodbare, sneridagh]

- Update <div id="content"> in all templates with <article id="content">
  [albertcasado]

- PLIP 14261: New resource registries.
  [bloodbare, vangheem, robgietema, et al]


5.0a2 (2014-04-20)
------------------

- Advertise the migration of content to dexterity after a successful
  upgrade to Plone 5.
  [pbauer]

- Strip leading & trailing spaces from id and title in rename-form.
  See https://dev.plone.org/ticket/12998, https://dev.plone.org/ticket/12989,
  https://dev.plone.org/ticket/9370, https://dev.plone.org/ticket/8338
  [pbauer]

- Fix incorrect use of dict get method in CatalogTool.search, introduced
  by PloneHotfix20131210 (issue 195)
  [fulv]

- Added timezone selection to add site page
  [pysailor, yenzenz]

- Added date date and time controlpanel (moved over from plone.app.event).
  [yenzenz. thet]

- Remove DL/DT/DD's from portal messages, portlet templates and others.
  Fixes `#153`_, `#163`_.
  [khink]

- PLIP 13260 remove templates and form scripts for
  ``select_default_page`` and ``select_default_view`` because they got
  migrated to browser views. Fix tests for that and remove legacy tests.
  See `#90`_.
  [saily]

- PLIP 13260: Migration contact-info to ``z3c.form`` and make it highly
  customizeable.
  [timitos, saily]


5.0a1 (2014-03-02)
------------------

- remove quickinstall control panel form since a new one was moved to
  plone.app.controlpanel
  [vangheem]

- Add 'warning' and 'error' status message types to the test_rendering
  view.
  [esteele]

- Update the front-page links.
  [esteele]

- In plone-overview view, we can now see Plone sites which are contained into
  Zope folder.
  [bsuttor]

- Make Plone tool read the exposeDCMetaTags from p.a.registry instead of
  of the site properties.
  [timo]

- Hide plone.app.registry install profile in the add-ons control panel.
  [esteele]

- Removed spamProtect.py script, since it doesn't offer real protection.
  [davisagli]

- Moved the member search form to plone.app.users
  [pabo3000]

- PLIP #13705: Remove <base> tag.
  [frapell]

- merge hotfixes from 20131210
  [vangheem]

- handle plone.app.textfield RichTextValue objects in syndication. Should
  fix syndication with plone.app.contenttypes.
  [vangheem]

- FolderFeed adapter now takes into account the limit property when displaying
  the RSS feed just like the other adapters do
  [ichim-david]

- Remove the portal_calendar tool and the dependency on CMFCalendar.
  [davisagli]

- Remove the plone_deprecated skin layer.
  [gforcada, davisagli]

- Moved portal_factory and portal_metadata from Products.CMFPlone to
  Products.ATContentTypes (PLIP #13770)
  [ale-rt]

- Remove the portal_interface tool.
  [ale-rt]

- Remove the portal_actionicons tool.
  [davisagli]

- Remove ownership_form and change_ownership script, which were not used.
  [davisagli]

- Convert author_feedback_template and accessibility_info to browser views.
  [bloodbare]

- Move calendar_macros and jscalendar to Products.Archetypes.
  [bloodbare]

- Remove plonetheme.classic from the package dependencies and the default
  extension profile, since it will not ship with Plone 5.
  [timo]

- Move docs/CHANGES.txt to CHANGES.rst.
  [timo]

- Replace deprecated test assert statements.
  [timo]

- Add a dependency on plone.app.theming. Install by default.
  [esteele]

- Drop dependency on plonetheme.classic.
  [esteele]

- Remove old logo.jpg. Use logo.png from Sunburst.
  [esteele]

- Inline validation JavaScript for z3c.form only sends request when
  field name can be obtained from DOM for a widget (#13741).
  [seanupton]

- Add use_uuid_as_userid site property.
  Part of PLIP 13419.
  [maurits]

- Let set_own_login_name use the update(Own)LoginName method from PAS.
  Part of PLIP 13419.
  [maurits]

- recently_modified and recently_published respects allow anonymous to view
  about setting
  [vangheem]

- Return a 404 instead of "AttributeError: (dynamic view)" if a user attempts to
  view a still-temporary PortalFactory item.
  [esteele]

- Ensure that initial_login is set to True when a user first logs in.
  [taito]

- Merged PLIP #12198: Depend on Chameleon (five.pt) as a faster page template
  engine.
  [davisagli]

- make extensionprofiles selection part of 'advanced' in plone-addsite
  [jaroel]

- enable syndication on plone.app.contenttypes collection
  [vangheem]

- fix syndication settings to not write on read
  [vangheem]

- fix wrong download url for podcast syndication
  [Rudd-O]

- Merged PLIP #12344: Use Dexterity-based core content types.

  * Avoid including ATContentTypes and Archetypes as a dependency.
  * Install the plone.app.contenttypes profile for new sites.

  [davisagli et al]

- Merged PLIP #13270: Move presentation mode out of core.
  If the feature is still desired, use the plone.app.s5slideshow add-on.
  [davisagli]

- Add "plone-5" ZCML feature. Add-ons can register
  ZCML for Plone 5 only using zcml:condition="have plone-5"
  [davisagli]

- Plone's javascript is now developed as part of the Plone mockup
  (http://github.com/plone/mockup) and is included as a compiled
  bundle.
  [davisagli]

- Removed portal_interface tool (PLIP #13770)
  [ale-rt]

- Removed kss_field_decorator_view support
  [maurits, jaroel]

.. _`commit 2d3865805efc6b72dce236eb68e502d8c57717b6`: https://github.com/plone/Products.CMFPlone/commit/2d3865805efc6b72dce236eb68e502d8c57717b6
.. _`commit bd1f9ba99d1ad40bb7fe1c00eaa32b8884aae5e2`: https://github.com/plone/Products.CMFPlone/commit/bd1f9ba99d1ad40bb7fe1c00eaa32b8884aae5e2
.. _`#78`: https://github.com/plone/Products.CMFPlone/issues/78
.. _`#90`: https://github.com/plone/Products.CMFPlone/issues/90
.. _`#153`: https://github.com/plone/Products.CMFPlone/issues/153
.. _`#163`: https://github.com/plone/Products.CMFPlone/issues/163
.. _`#216`: https://github.com/plone/Products.CMFPlone/issues/216
.. _`#220`: https://github.com/plone/Products.CMFPlone/issues/220
.. _`#290`: https://github.com/plone/Products.CMFPlone/issues/290
.. _`#350`: https://github.com/plone/Products.CMFPlone/issues/350
.. _`#411`: https://github.com/plone/Products.CMFPlone/issues/411
.. _`#454`: https://github.com/plone/Products.CMFPlone/issues/454
.. _`#550`: https://github.com/plone/Products.CMFPlone/issues/550
.. _`#553`: https://github.com/plone/Products.CMFPlone/issues/553
.. _`#557`: https://github.com/plone/Products.CMFPlone/issues/557
.. _`#558`: https://github.com/plone/Products.CMFPlone/issues/558
.. _`#573`: https://github.com/plone/Products.CMFPlone/issues/573
.. _`#604`: https://github.com/plone/Products.CMFPlone/issues/604
.. _`#862`: https://github.com/plone/Products.CMFPlone/issues/862
.. _`#886`: https://github.com/plone/Products.CMFPlone/issues/886
.. _`#895`: https://github.com/plone/Products.CMFPlone/issues/895
.. _`#913`: https://github.com/plone/Products.CMFPlone/issues/913
.. _`#918`: https://github.com/plone/Products.CMFPlone/issues/918
.. _`#926`: https://github.com/plone/Products.CMFPlone/issues/926
.. _`#935`: https://github.com/plone/Products.CMFPlone/issues/935
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
