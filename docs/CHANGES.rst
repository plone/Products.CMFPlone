.. This file should contain the changes for the last release only, which
   will be included on the package's page on pypi. All older entries are
   kept in HISTORY.txt

Changelog
=========

4.3.10 (unreleased)
-------------------

- New:

- *add item here*

Fixes:

- Render correct links in form-tabs, so they can be opened with right-mouse-click and
  correct tab is selected, when using anchor-hashes. Fixes #1640.
  [ida]

- jquery.highlightsearchterms.js was skipping words that simply *contains* reserved ``filterTerms`` terms.
  [keul]

- Render an empty ``<dd>`` tag on ``folder_listing`` template when no description is available to avoid validation issue.
  [hvelarde]

- Removed docstrings from PropertyManager methods to avoid publishing them.  [maurits]

- Added publishing patch from Products.PloneHotfix20160419.
  This avoids publishing some methods inherited from Zope or CMF.  [maurits]

- Removed docstrings from some methods to avoid publishing them.  [maurits]

- Ensured front-page is English when creating an English site.
  Previously, when creating an English site with a browser that
  prefers a different language, the body text ended up being in the
  browser language.  For languages without a front-page text
  translation the same happened: they got the other language instead
  of English.  [maurits]


4.3.9 (2016-03-29)
------------------

- No changes


4.3.8 (2016-03-08)
------------------

Fixes:

- Add dl.portalMessage.warning to common_content_filter in popupforms.js so
  warnings get also pulled into the popup. [pcdummy]

- Disabled CSRF protection on site creation form and upgrade form.  [maurits]

- When migration fails, do not upgrade addons or recatalog or
  update roles.
  [maurits]

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

- Add syndication for plone.app.contenttypes collections.
  [do3cc]

- Add CSRF authenticator in createObject script
  [ebrehault]

- Let set_own_login_name use the update(Own)LoginName method from PAS.
  Part of PLIP 13419.
  [maurits]

4.3.7 (2015-09-27)
------------------

- Remove Chrome Frame from ``X-UA-Compatible`` HTTP header as it's deprecated.
  [hvelarde]

- Apply hotfixes from https://pypi.python.org/pypi/Products.PloneHotfix20150910
  [vangheem]

- Do not throw a 404 on site root RSS feeds
  [vangheem]

- Upgrade known core packages at the end of the Plone migration.
  [maurits]

- Require ``POST`` request for various forms that send email.
  [maurits]

- Make the `formUnload.js` protection works while using CKEditor
  as it is the case with TinyMCE.
  [gbastien]

- Properly hide ``plone.app.jquery`` and ``plone.app.jquerytools``
  from products.
  [maurits]

- Fix email validation of long domain names.
  [gotcha]


4.3.6 (2015-06-02)
------------------

- Release Plone 4.3.6 to correct some version incompatibilities in 4.3.5. No upgrades to run.
  [esteele]

- fix syndication settings to not write on read
  [vangheem]

4.3.5 (2015-05-13)
------------------

- Implement new feed syndication using `NewsML 1 <http://iptc.org/standards/newsml-1/>`_,
  an IPTC standard that provides a media-type-independent, structural framework for multi-media news.
  [frapell, jpgimenez, tcurvelo]

- Add tests for configuring encoding of user registration or
  forgotten password emails.
  [davidjb]

- Pass email encoding to forgotten password email template.
  [davidjb]

- Pass mail ``Content-Type`` to mailhost when sending forgotten password
  emails.
  [davidjb]

- Fix: If a user "deletes" the same item twice (ex.: having two different tabs
  open and not realising it's already been deleted) any higher level item with
  the same short name will be deleted without trace.
  [gotcha]

- Extended ulocalized_time for target_language
  [agitator]

- Allow search_rss view on subsites (implementing INavigationRoot, not only
  IPloneSiteRoot) like it was the case in Plone 4.1.6.
  [vincentfretin]

- jQuery 1.9 compatibility for the toggleSelect function (Select all checkbox)
  [vincentfretin]

- Sharing view javascript now works with jQuery 1.9.
  [vincentfretin]


4.3.4.1 (2014-11-13)
--------------------

- Make inline validation of AT multiple selection widget work.
  [gbastien]


4.3.4 (2014-10-22)
------------------

- Fix getFolderContents to no longer ignore 'show_inactive' in contentFilter.
  This is part of a fix for https://dev.plone.org/ticket/8353.
  [pbauer]

- Fix link to the mail_password_form on the login_form for sites using VHM
  [fRiSi]

- folder_position script: make position and id optional.  Default
  position to 'ordered' and id to None, which means: do nothing.
  plone.folder 1.0.5 allows this, making it possible to simply reverse
  the current sort order by using reverse=False.
  [maurits]

- Abstract the search form and livesearch action URLs making it easier to
  extend the search portlet with custom views or other actions.
  [rpatterson]

- Declare minimum plone.app.jquery dependency (1.7.2) in setup.py.
  [thet]

- Fix JavaScript to work with recent jQuery (>= 1.9) versions.
  [thet]

- Improve event_view - do not show time when user specifies the same start and
  end time for an event.
  [spereverde]

- Fix for https://dev.plone.org/ticket/13603 would break with VHM.
  [spereverde, jakke, jfroche]

- Strip leading & trailing spaces from id and title in rename-form.
  See https://dev.plone.org/ticket/12998, https://dev.plone.org/ticket/12989,
  https://dev.plone.org/ticket/9370, https://dev.plone.org/ticket/8338
  [pbauer]

- Add 'warning' and 'error' status message types to the test_rendering
  view.
  [esteele]

- In plone-overview view, we can now see Plone sites which are contained into
  Zope folder.
  [bsuttor]

- Fixed plone.css and plone.session integration. Do not break when not found
  resources are registered in the portal_css tool
  [keul]

- Small scoping fix in locking js code
  [do3cc]


4.3.3 (2014-02-19)
------------------
- Fix incorrect use of dict get method in CatalogTool.search, introduced by
  PloneHotfix20131210 (issue 195)
  [fulv]

- Change default permission for sendto_form to Authenticated instead of
  Anonymous
  [vangheem]

- merge hotfixes from https://pypi.python.org/pypi/Products.PloneHotfix20131210
  [vangheem]

- handle plone.app.textfield RichTextValue objects in syndication. Should
  fix syndication with plone.app.contenttypes.
  [vangheem]

- FolderFeed adapter now takes into account the limit property when displaying
  the RSS feed just like the other adapters do
  [ichim-david]

- Fix handling of URL fragments in form_tabbing.js.
  [davisagli]

- Password reset emails will now be sent from the navigation root instead
  the portal, enabling support for multilingual sites and other subsites
  to keep the correct language, title, menus and designs.
  [regebro]

- Fix issue where a user could delete unintended object through
  acquisition magic. See https://dev.plone.org/ticket/13603.
  [gotcha]

- Added a method toLocalizedSize to @@plone view,
  on the model of toLocalizedTime,
  to get a localized string rendering a size from an integer.
  Use it on image view.
  [thomasdesvenain]

- Remove plone_deprecated/sitemap.pt to avoid sitemap traceback because we
  don't have a @@sitemap_view view anymore when you enable back
  the plone_deprecated skin layer.
  [vincentfretin]

- Inline validation JavaScript for z3c.form only sends request when
  field name can be obtained from DOM for a widget (#13741).
  [seanupton]

- Fix problem generating feeds including Dexterity items with no primary field.
  [bloodbare]

- recently_modified and recently_published respects allow anonymous to view
  about setting
  [vangheem]

- Return a 404 instead of "AttributeError: (dynamic view)" if a user attempts to
  view a still-temporary PortalFactory item.
  [esteele]

- Ensure that initial_login is set to True when a user first logs in.
  [taito]

- No longer set news, events and member folder to be unordered
  [vangheem]

- Fix calendar ajax next and prev buttons
  [vangheem]

- Ensure ``object_rename`` script has ``_`` message factory available
  to prevent error when unauthorized.
  [davidjb]

- Fix issue with the search js in sharing page where the user needed to check
  twice a checkbox to assign a role after a search.
  [vincentfretin]

- Catch missing userid on mail_password form, and treat is as
  an empty userid. That way the user gets a helpful message.
  [do3cc]

- If a page is renamed and the page is a default page, default page setting is corrected
  [hoka]


4.3.2 (2013-08-14)
------------------

- fix wrong download url for podcast syndication
  [Rudd-O]

- Applied security fixes from PloneHotfix20130618:

  - Protected methods on the ZCatalog.
  - Added missing module security declarations.
  - Sanitize url in isURLInPortal.
  - Check 'Set own password' permission in mailPassword.
  - Prevent the Zope request from being traversed.
  - Protected sendto method.
  - Sanitize input to spamProtect script.

  [davisagli]

- Get ``portal_discussion`` properly with ``getToolByName``.
  [maurits]

- Fix dependency ordering problem with plone-final import step.
  [davisagli]

- remove bbb-kss.css from css registry registration
  [vangheem]

- Stop unload-protection from popping up needlessly if tinyMCE is used on tabbed forms
  [href]

4.3.1 (2013-05-30)
------------------

- Some text/* mime types should be Files, not Documents.
  [rpatterson]

- Remove reference to unimplemented 'make_private' transition in
  simple_publication_workflow.
  [danjacka]

- Fail nicely when pasting a deleted item (https://dev.plone.org/ticket/13337)
  [khink]

- Add a 'max_tabs' option to form-tabbing.js to allow changes to the number of
  tabs displayed before the script uses a dropdown instead.
  [esteele]

- register search_rss only for site root
  [vangheem]

- jquery-integration.js gets disabled during the upgrade to Plone 4.3. Make sure
  we do so for new sites as well.
  [esteele]

- Fix commas in kss-bbb.js since IE7/8 is sensative [vangheem]

- Reenable forgotten tests [kiorky]

- Fail nicely when userid is not provided to mail_password script.
  [esteele]

- Do not display text file content if it is empty.
  [thomasdesvenain]

- Add distinct classes for live search links.
  Add id for image details.
  [cedricmessiant]

- update registerPloneFunction call in login.js (depreacted)
  [toutpt]

4.3 (2013-04-06)
----------------

- Fix attribute values in selector expressions of  mark_special_links.js.
  [mathias.leimgruber]

- Add indexer for location so metadata is included in catalog
  [vangheem]

- Fix rss 2.0 not providing actual link
  [vangheem]

- Prevent js inline validation call to /at_validate_field for .blurrable
  inputs that do not have AT field data validation attributes. This
  avoids cluttering the error logs with useless at_validate_field
  errors for fields that just happen to have .blurrable class.
  [mcmahon]

- Test for #7627 (https://dev.plone.org/ticket/7627)

4.3rc1 (released)
-----------------

- add overlay for folder default page folder factories link
  [vangheem]

- add sitemap.xml.gz to robots.txt fixes https://dev.plone.org/ticket/13319
  [vangheem]

- update add site, overview and upgrade templates to use absolute urls
  to reference css and image resources so it works with virtual hosted
  sites to sub-folders fixes #11153
  [vangheem]

- Allow the Content-Type header to be set in registered_notify_template.pt
  [esteele]

- Extract RegistrationTool's sending of registration emails so that it can be
  more easily overridden.
  [esteele]

- bump profile version
  [vangheem]

- Add event to fix products installed with latest keyword
  activated by default. Event finds new products installed with
  the latest keyword and updates them to the last profile version.
  [eleddy]

- Add event to trigger when a reordering is happening. Without this
  collective.solr and maybe other alternative indexes are kind of lost.
  Backport from 4.2.x
  [do3cc]

- Robot Framework based acceptance tests added.
  [timo]

- Remove comment form overlay which was only used for the old
  pre-plone.app.discussion reply form.
  [timo]


4.3b2 (2013-01-17)
------------------

- removing ``plone_ecmascript/test_ecmascripts.pt`` since its not working and
  since its not being ran by out test suite.
  [garbas]

- Call searchUsers with the 'name' argument instead of 'login'.
  'name' is the officially supported way according to the PAS interface.
  [maurits]


4.3b1 (2012-01-02)
------------------

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

.. _`#1041`: https://github.com/plone/Products.CMFPlone/issues/1041
