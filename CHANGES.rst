.. This file should contain the changes for the last release only, which
   will be included on the package's page on pypi. All older entries are
   kept in HISTORY.txt

Changelog
=========

5.0a1 (unreleased)
------------------

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
