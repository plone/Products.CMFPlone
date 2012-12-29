.. This file should contain the changes for the last release only, which
   will be included on the package's page on pypi. All older entries are
   kept in HISTORY.txt

Changelog
=========


4.3a3 (unreleased)
------------------

- removing ``plone_ecmascript/test_ecmascripts.pt`` since its not working and
  since its not being ran by out test suite.
  [garbas]

- Changes to dependencies when creating a new site (plone-final) to fix
  #11997.
  [keul]

- Generate valid atom feeds
  [lentinj]

- Fix quoted atom.xml feed syndication content type to "html".
  [elro]

- Add various security fixes based on PloneHotfix20121106.
  [davisagli]

- Fix RegistrationTool testPasswordValidity method. See
  https://dev.plone.org/ticket/13325
  [vipod]

- Fix form_tabbing.js so it stays on the same fieldset when an Archetypes
  edit form is submitted and returns to itself.
  [davisagli]

- Use the 'OFS.ObjectManager.bad_id' pattern in 'PloneTool.BAD_CHARS'.
  This allows names containing '@' to pass 'check_id'.
  [elro]

- Pass minute_step to date_components_support_view.result(). See
  https://dev.plone.org/ticket/11251
  [gbastien]

- Improve error handling on paste action. If it is a real error, the
  error gets shown and logged.
  [do3cc]

- Fix sitemap rendering. No longer uses portlet_navtree_macro.pt from
  the plone_deprecated skin, but a browser view template with much
  simplified logic.
  [danjacka]

- Revealed hidden features for sorting folders (#11317).
  [keul]

- Don't swallow exceptins on object_paste and folder_paste (#9365).
  [gaudenz]

4.3a2 (2012-10-18)
------------------

- Use prefixed ids for popup overlays
  [maartenkling]

- Fix compatible hide fieldset legend for IE6/7/8 in form_tabbing.js
  [maartenkling]

- Add an animated indicator of AJAX loading via Javascript.
  It is now called #ajax-spinner and is no longer added in main_template.
  [davisagli]

- Remove Plone's dependency on KSS. plone.app.kss is now an optional add-on.
  Functionality that used to be provided using KSS has been reimplemented.
  [esteele, vangheem, cah190, davisagli]

- Do not block right-side portlets in Members folder on site creation.
  This fixes https://dev.plone.org/ticket/10764
  [polyester]

- Fix prefs_install_product_readme so files with non-ascii characters are
  rendered. This fixes https://dev.plone.org/ticket/12342
  [ericof]

- Fix StringIO module security so it can still be imported from restricted
  code in Zope 2.13.17+.
  [davisagli]

- Filter out non existing types in getUserFriendlyTypes.
  This avoids an error on the search form when a no longer existing
  portal_type is still in the catalog.
  [maurits]

- Declare Plone's dependency on Pillow.
  [davisagli]

- Merge syndication plip 12908
  [vangheem]

- Add body class depth registry field
  [vangheem]

- Check if an item is locked before attempting to delete. Refs #11188
  [eleddy]

- We can safely move the MAX_TITLE to 50 and even move up MAX_DESCRIPTION 150 refs #11321
  [maartenkling]

- Remove inline styles, they do nothing, add class so someone can style it when they like refs #12438
  [maartenkling]

- Show forget password when entering wrong credentials refs #12463
  [maartenkling]

- Remove h3 to make consistent html refs #11344
  [maartenkling]

- Fix 'Add New' on Users/Groups Overviews shows overlay when clicking anywhere in form #12201
  [maartenkling]

- Fix events_listing #12477
  [maartenkling]

- Fix form_tabbing, to stay on current tab on submitting form
  [maartenkling]


4.3a1 (2012-08-31)
------------------

- Hide 'plone.resource' and 'collective.z3cform.datetimewidget' from the
  site factory screen. These are only useful as dependencies of other packages.
  [optilude]

- Define a ZCML feature called `plone-43` in addition to the existing ones.
  [thet]

- Deprecated getSiteEncoding and changed occurences to hardcoded `utf-8`
  [tom_gross]

- zope.globalrequest is a required dependency on tests.
  [hvelarde]

- Make sure the ResourceRegistries registry setting is created for new sites.
  [davisagli]

- Searches ignore accents.
  PLIP http://dev.plone.org/ticket/12110
  [thomasdesvenain]

- IE critical fix on toggle select and form submit helpers.
  [thomasdesvenain]

- Fixed javascript injections on jquery.highlightsearchterms.js
  [gborelli]

- Tweak rules for `sortable_title`. So far we took the first 70 chars and
  zero-padded numbers to six digits. Now we zero-pad to four digits and take
  the first 30 and the last 10 characters, thus saving space while still
  distinguishing long titles which only differ at the end, like imported
  file or image names.
  [hannosch]

- PEP 8 (ignoring W602, E203, E241, E301, E501 and E701).
  [pbdiode, hvelarde]

- Add 'displayPublicationDateInByline' to site properties property sheet in
  order to finish PLIP #8699: Display publication date in author byline.
  [vipod]

- Deprecated aliases were replaced on tests.
  [hvelarde]

- Don't register the plone_deprecated skin layer. These items are no
  longer supported as part of Plone and remain here temporarily as a
  convenience to those who may need to move them into their own
  packages.
  [davisagli]

- Ensure multiple tabbed forms on the same page work when number of
  tabs is greater than threshold.
  [davidjb]

- Remove deprecated `jq` reference from form tabbing JavaScript.
  [davidjb]

- Remove incorrect line of form tabbing JavaScript which broke
  forms with more than 6 tabs.
  Fixes https://dev.plone.org/ticket/12877
  [davidjb]

- accessibility improvements for screen readers regarding "more" links,
  see http://dev.plone.org/ticket/11982
  [rmattb, applied by polyester]

- Fix an outdated "Send this" form handler property reference.
  [rossp]

- removed search_form-template form plone_deprecated-skin. Use
  collective.searchform if you need this functionality.
  [tom_gross]

- Use plone.batching for all batches (PLIP #12235)
  [tom_gross]

- Re-apply PLIP 10901 to table_sort.js, fixing a bug with reversing sort
  on the first column.
  [mj]

- support a PAS plugin for validating passwords
  PLIP http://dev.plone.org/ticket/10959
  [djay75]

- Make redirection_view/attempt_redirect fall back to nothing in
  default_error_message template. If plone.app.redirector gets a URL with
  special characters, OOBTree.get raises a UnicodeDecodeError and the template
  fails. This fixes http://dev.plone.org/ticket/12976.

- Channel link in RSS feed now points to the un-syndicated content for the RSS feed,
  instead of the portal root.
  [patch by pydanny, applied by kleist]

- Removed unused "localTimeFormat", "localLongTimeFormat", and "localTimeOnlyFormat"
  from "/portal_properties/site_properties".
  Fixes https://dev.plone.org/ticket/11171.
  [kleist]

- CatalogTool.py, PloneBatch.py, PloneFolder.py, PloneTool.py, Portal.py:
  Don't use list as default parameter value.
  [kleist]

- Use configuration registry to override translation of date format,
  or fall back to ISO style as last resort. Fixes http://dev.plone.org/ticket/11171
  [kleist]
