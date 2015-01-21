.. This file should contain the changes for the last release only, which
   will be included on the package's page on pypi. All older entries are
   kept in HISTORY.txt

Changelog
=========

5.0b1 (unreleased)
------------------

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
