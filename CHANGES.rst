.. This file should contain the changes for the last release only, which
   will be included on the package's page on pypi. All older entries are
   kept in HISTORY.txt

Changelog
=========

5.0rc2 (unreleased)
-------------------

- Move login properties to the configuration registry.
  [esteele]

- Fix changing searchable in types-controlpanel.
  Fix https://github.com/plone/Products.CMFPlone/issues/926
  [pbauer]

- Respect view-url in livesearch-results. Fixes #918.
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

- fix #862: Profile listing on site creation has alignment issues
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
  Fixes https://github.com/plone/Products.CMFPlone/issues/604
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

- fix #350: "plone.app.content circular dependency on Products.CMFPlone" - this
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

- Fix adding a new Plone site with country specific language. Refs #411.
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
  Fixes https://github.com/plone/Products.CMFPlone/issues/573
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

- Do not require "Enable LiveSearch". This fixes https://github.com/plone/Products.CMFPlone/issues/558
  [timo]

- Fix control panel titles. This fixes https://github.com/plone/Products.CMFPlone/issues/550 https://github.com/plone/Products.CMFPlone/issues/553 https://github.com/plone/Products.CMFPlone/issues/557
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
  param onto url. See https://github.com/plone/Products.CMFPlone/commit/2d3865805efc6b72dce236eb68e502d8c57717b6
  and https://github.com/plone/Products.CMFPlone/commit/bd1f9ba99d1ad40bb7fe1c00eaa32b8884aae5e2
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

- Make typesToList read metaTypesNotToList from new p.a.registry settings.
  This fixes https://github.com/plone/Products.CMFPlone/issues/454.
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

- Move security control panel to CMFPlone. Fixes #216.
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

- Move markup control panel to CMFPlone. Fixes #220.
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
  https://github.com/plone/Products.CMFPlone/issues/290
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

- PLIP 13260: Migrate author page to browser views/z3c.form (issue #78)
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
  https://github.com/plone/Products.CMFPlone/issues/153
  https://github.com/plone/Products.CMFPlone/issues/163
  [khink]

- PLIP 13260 remove templates and form scripts for
  ``select_default_page`` and ``select_default_view`` because they got
  migrated to browser views. Fix tests for that and remove legacy tests.
  See: https://github.com/plone/Products.CMFPlone/issues/90
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
