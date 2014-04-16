.. This file should contain the changes for the last release only, which
   will be included on the package's page on pypi. All older entries are
   kept in HISTORY.txt

Changelog
=========

5.0a2 (unreleased)
------------------

- Added timezone selection to add site page
  [pysailor, yenzenz]

- Added date date and time controlpanel (moved over from plone.app.event).
  [yenzenz. thetet]

- Remove DL/DT/DD's from portal messages, portlet templates and others.
  https://github.com/plone/Products.CMFPlone/issues/153
  https://github.com/plone/Products.CMFPlone/issues/163
  [khink]

-  PLIP 13260 remove templates and form scripts for
   ``select_default_page`` and ``select_default_view`` because they got
   migrated to browser views. see:
   https://github.com/plone/Products.CMFPlone/issues/90
   [saily]

- PLIP 13260: Migration contact-info to z3c.form and make it highly
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
