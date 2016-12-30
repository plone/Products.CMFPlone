Changelog
=========

2.6.3 (2016-12-30)
------------------

Bug fixes:

- Fix sitemap.xml.gz for plone.app.multilingual (>= 2.x) but breaks it for
  LinguaPlone and plone.app.multilingual 1.x
  If this is a problem then please see bedbfeb67 on 2.5.x branch for how to
  maintain compatibility with these products.
  [djowett]

- Include the ``template`` body class also, when a view but no template is passed.
  Fixes missing template class with plone.app.blocks based layouts in Mosaic.
  [thet]


2.6.2 (2016-11-18)
------------------

Bug fixes:

- Removed ZopeTestCase from the tests.
  [ivanteoh, maurits]

- Add default icon for top-level contentview toolbar entries
  [alecm]

- Remove commented out viewlet (meant for Plone 3) and its related template.
  [gforcada]

- Adapt code to some deprecated methods getting finally removed.
  [gforcada]


2.6.1 (2016-06-07)
------------------

Bug fixes:

- Document byline viewlet is now displayed only to anonymous users if permited by the `Allow anyone to view 'about' information` option in the `Security Settings` of `Site Setup` (closes `CMFPlone#1556`_).
  Code used to show the lock status and history view was removed from the document byline as this information was not available to anonymous users anyway.
  [hvelarde]


2.6.0 (2016-05-10)
------------------

Incompatibilities:

- Deprecated ``plone.app.layout.globals.pattern_settings``.
  Moved view to ``Products.CMFPlone.patterns.view``.
  Deprecated also pointless interface for this view.
  Addresses https://github.com/plone/Products.CMFPlone/issues/1513 and goes together with https://github.com/plone/Products.CMFPlone/issues/1514.
  [jensens]

Fixes:

- Fix body class ``pat-markspeciallinks`` not set.
  Fixes #84.
  [thet]

2.5.19 (2016-03-31)
-------------------

New:

- Construct the site logo URL to be rooted at ISite instances returned by
  ``zope.component.hooks.getSite`` and not only rooted at portal root.
  This makes it possible to have sub sites with local registries which return
  a different logo.
  [thet]

Fixes:

- Fixed html validation: element nav does not need a role attribute.
  [maurits]

- Fixed invalid html of social viewlet by moving the schema.org tags
  to the body in a new viewlet ``plone.abovecontenttitle.socialtags``
  and adding ``itemScope`` and ``itemType`` there.
  Fixes https://github.com/plone/Products.CMFPlone/issues/1087
  [maurits]

- Fix test isolation problems: if a test calls transaction.commit() directly or
  indirectly it can not be an integration test, either avoid the commit or
  change the layer into a functional one.
  Fixes: https://github.com/plone/plone.app.layout/issues/79
  [gforcada]


2.5.18 (2016-02-11)
-------------------

New:

- Switched deprecated ``listingBar`` CSS class to ``pagination``.
  [davilima6]

Fixes:

- Adapted to changed Zope 4 ``browser:view`` semantics.  We either
  need a ``template`` ZCML argument or a ``__call__`` method on the
  class.  [thet]


2.5.17 (2015-11-26)
-------------------

New:

- Added option to show/hide thumbs in site-controlpanel.
  https://github.com/plone/Products.CMFPlone/issues/1241
  [fgrcon]

Fixes:

- Fixed missing closed span in document_relateditems.pt.
  [vincentfretin]

- Fixed relatedItemBox: show thumbs, title and description correctly.
  https://github.com/plone/Products.CMFPlone/issues/1226
  [fgrcon]


2.5.16 (2015-10-28)
-------------------

Fixes:

- Removed Chrome Frame from ``X-UA-Compatible`` HTTP header as it's deprecated.
  [hvelarde]

- Fixed icon rendering.  Issue `CMFPlone#1151`_.
  [fgrcon]

- Fixed global sections tabs.  Issue `CMFPlone#1178`_.
  [tomgross]


2.5.15 (2015-09-20)
-------------------

- Pull mark_special_links, external_links_open_new_window,
  types_view_action_in_listings values
  from configuration registry.
  [esteele]

- Respect @@site_controlpanel configuration to show publication date
  in document_byline.  Closes `CMFPlone#1037`_.
  [rodfersou]

- Implemented fuzzy dates for document_byline.  Closes `CMFPlone#1000`_.
  [rodfersou]


2.5.14 (2015-09-15)
-------------------

- add icons-off body class for icon setting
  [vangheem]

- Use global site-title for og:site_name.
  Fixes https://github.com/plone/Products.CMFPlone/issues/951
  [pbauer]


2.5.13 (2015-09-12)
-------------------

- Fixed AttributeError for ac_permissions.
  Happens in plone.app.portlets tests.
  [maurits]


2.5.12 (2015-09-08)
-------------------

- Bring back document byline.  Closes `CMFPlone#741`_.
  [rodfersou]


2.5.11 (2015-09-07)
-------------------

- Be more defensive in getting registry settings so upgraded
  schema does not cause errors
  [vangheem]

- Pull values for display_publication_date_in_byline, default_language,
  icon_visibility from the configuration registry.
  [esteele]

2.5.10 (2015-08-20)
-------------------

- Correctly display selected item in global navigation for images and files.
  Fixes https://github.com/plone/Products.CMFPlone/issues/830
  [pbauer]

- Add view url to document as data-view-url
  [ale-rt]

- If toolbar logo is empty, use default
  [vangheem]

- Move getDefaultPage, isDefaultPage, IDefaultPage and DefaultPage view to
  Products.CMFPlone in order to avoid circular imports between both packages.
  Moved test for it as well. Placed deferred deprecated imports for all old
  names here.
  [jensens]

- Remove deprecated ``context`` parameter from ``DefaultPage`` methods.
  [jensens]

- minor cleanup in getDefaultPage function
  [jensens]

- Added a test for the complex getDefaultPage function
  [jensens]

2.5.9 (2015-07-21)
------------------

- Default is expanded Toolbar.
  [bloodbare]


2.5.8 (2015-07-18)
------------------

- Moved historyRecords in @@historyview into a table
  [agitator]

- Combine viewlets used in the IToolbar viewlet manager, merge, reorder
  items so they make more sense
  [vangheem]

- merge plone.personal_bar viewlet into toolbar viewlet manager
  [vangheem]

- remove plone.contentactions, merged into ContentViewsViewlet
  [vangheem]

- remove plone.documentbyline as it wasn't really a viewlet anymore and we
  were force rendering it into toolbar viewlet manager
  [vangheem]

- remove "you are here" in breadcrumbs
  [vangheem]

- always show site root syndication links if enabled
  [vangheem]

- by default, show site logo in social settings
  [vangheem]

- Add aria hidden role to avoid screenreaders to nonesense stop by at the
  toolbar tiny logo [sneridagh]

- Get rid completely of the plone.skip_links viewlet because it already doesn't
  worked OOTB since always and this does not follow modern a11y methods and we
  are dropping support for outdated ways [sneridagh]

- Remove all references to "accesskeys" attributes on templates [sneridagh]

- Disabled document_byline viewlet in favor of toolbar action.
  [agitator]

- Added documentByLine to @@historyview
  [agitator]

- removed DocumentBylineViewlet
  [agitator]


2.5.7 (2015-06-05)
------------------

- Add social meta tags viewlet
  [vangheem]

- render the footer portlets in a way where they can still
  be edited with @@manage-portlets
  [vangheem]


2.5.6 (2015-05-13)
------------------

- do not set width and height on logo
  [vangheem]

- provide active class for currently selected toolbar item
  [vangheem]

- Add ``_authenticator`` param to contenthistory URLs.
  This will prevent CSRF warnings
  (see https://github.com/plone/Products.CMFPlone/issues/330)
  [keul]

2.5.5 (2015-05-04)
------------------

- Updating tests to handle new plone.app.testing.
  [do3cc]

- Fix info_empty_dashboard i18n default message.
  [vincentfretin]

- Add row class to constrain width of footer.
  [davisagli]

- pat-modal pattern has been renamed to pat-plone-modal
  [jcbrand]


2.5.4 (2015-03-13)
------------------

- Read ``allow_anon_views_about`` settings from the registry instead of portal
  properties (see https://github.com/plone/Products.CMFPlone/issues/216).
  [jcerjak]

- use livesearch pattern
  [vangheem]

- use configuration registry pattern options
  [vangheem]

- Added support for site logos stored in the portal registry via the site
  control panel for the logo viewlet with a fallback to the ``OFS.Image``
  based ``logo.png`` file. Removed support of long-gone
  ``base_properties.props`` defined logo names.
  [thet]

- Updated markup for dashboard.
  [davisagli]

- Add pat-markspeciallinks to bodyClass depending on settings in @@theming-controlpanel.
  [fulv]

- Fix relateditems viewlet (tal:repeat is executed after tal:define).
  [pbauer]


2.5.3 (2014-11-01)
------------------

- Move patterns settings to CMFPlone
  [bloodbare]

- Initial implementation of Mockup-aware content info section.
  [sneridagh]


2.5.2 (2014-10-23)
------------------

- Switch site_title setting from root property to p.a.registry.
  [timo]

- Switch webstats_js setting from site_properties to p.a.registry.
  [timo]

- Switch enable_sitemap setting from site_properties to p.a.registry.
  [timo]

- Fix related items viewlet listing dexterity related folder's descendants.
  [rpatterson]

- Add more data attributes to body tag
  [vangheem]

- Change document byline viewlet manager to toolbar. Adapt template for toolbar.
  [sneridagh]

- Update byline viewlet name.
  [sneridagh]

- Created new viewlet manager for holding main navigation for a more semantic
  use of it. Move the global sections viewlet into it.
  [albertcasado]

- Update and cleaning History markup popup.
  [bloodbare]

- Updated global navigation and breadcrumbs markup. Added ARIA roles.
  [bloodbare]

- New toolbar markup based in ul li tags.
  [albertcasado, bloodbare, sneridagh]

- Update <div id="content"> in all templates with <article id="content">
  [albertcasado]

- Added new class to the body tag via globals layout bodyClass method. This is
  used for maintain the consistency of the selected toolbar state.
  [sneridagh]


2.5.1 (2014-04-05)
------------------

- Remove DL, DT and DD elements
  https://github.com/plone/Products.CMFPlone/issues/153
  [khink, mrtango]

- for contentview urls, add csrf token automatically
  [vangheem]

- Add content url to document as data-base-url
  [do3cc]


2.5.0 (2014-03-02)
------------------

- Switch webstats_js setting from site_properties to p.a.registry.
  (PLIP #10359: http://dev.plone.org/ticket/10359)
  [timo]

- Switch enable_sitemap setting from site_properties to p.a.registry.
  (PLIP #10359: http://dev.plone.org/ticket/10359)


2.4a1 (unreleased)
------------------

- PLIP #13705: Remove <base> tag.
  [frapell]

- Make the link to plone.org open in a new tab/window.
  [Toni Mueller]

- Fix body class attribute errors when the user role contains space.
  [Jian Aijun]

- Remove dependency on unittest2 as we are not going to test against
  Python 2.6 anymore on Plone 5.0.
  [hvelarde]

- Update package dependencies and clearly specify this branch is for
  Plone >=4.3 only (in fact, should be 5.0).
  [hvelarde]

- Fix 'plone.belowcontentbody.relateditems' viewlet to avoid trying to
  display items if the user has no permission to view them (like content
  in Private state).
  [hvelarde]

- Migrate portal_interface tool methods to plone_interface_info (PLIP #13770).
- Remove deprecated portal_interface tool (PLIP #13770).
  [ale-rt]

- Remove outdated and unused discussion code and tests.
  [timo]

- Use logo.png instead of logo.jpg
  [esteele]

- Add plone.app.relationfield to test dependencies,
  needed to test dexterity support. [jpgimenez]

- Don't break if None is passed as the template to bodyClass.
  [davisagli]

- Use tableofcontents-viewlet for plone.app.contenttypes
  Fixes https://github.com/plone/plone.app.contenttypes/issues/34
  [pbauer]

- Remove presentation mode. If the feature is still desired use
  the plone.app.s5slideshow add-on.
  [davisagli]

- PEP8 cleanup.
  [timo]

- modified sections.pt for adding link target.
  Fixed that portal_actions: 'Link Target' on
  portal_actions/portal_tabs doesn't work.
  [terapyon]

- Ported tests to plone.app.testing
  [tomgross]


2.3.13 (2015-04-30)
-------------------

- Fix: in test passing portal to addMember, not testcase class.
  [jensens]


2.3.12 (2014-09-07)
-------------------

- Fix related items viewlet listing dexterity related folder's descendants.
  [rpatterson]


2.3.11 (2014-02-19)
-------------------

- Update package dependencies and clearly specify this branch is for
  Plone 4.3 only.
  [hvelarde]


2.3.10 (2013-11-13)
-------------------

- Fix 'plone.belowcontentbody.relateditems' viewlet to avoid trying to display
  items if the user has no permission to view them (like content in Private
  state).
  [hvelarde]

- modified sections.pt for adding link target.
  Fixed that portal_actions: 'Link Target' on
  portal_actions/portal_tabs doesn't work.
  [terapyon]

- Add plone.app.relationfield to test dependencies,
  needed to test dexterity support. [jpgimenez]


2.3.9 (2013-09-25)
------------------

- Removed hard dependency on plone.app.relationfield.
  [pabo, marcosfromero]


2.3.8 (2013-09-16)
------------------

- Fix 'table of contents' for Dexterity types.
  [pabo, pbauer, timo]

- Use safe_unicode to decode the title of the object when retrieving the rss
  links from the RSSViewlet.
  [ichim-david]


2.3.7 (2013-08-14)
------------------

- Don't try to getId() for the template-name body when there is no template.
  Corrects an issue with the Dexterity schema editor.
  [esteele]


2.3.6 (2013-08-13)
------------------

- Fix conflict with <body> class attribute improvement in TinyMCE.
  [rpatterson]

- Implement a canonical link relation viewlet to be displayed by
  IHtmlHeadLinks viewlet manager; this will prevent web indexers from indexing
  the same object more than once, improving also the way these indexers deal
  with images and files.
  [hvelarde]

- Add Dexterity support for the related items viewlet.
  [pabo]

- Personal bar viewlet home link simply links to the user actions list.
  [danjacka]


2.3.5 (2013-05-23)
------------------

- Fixed AttributeError for FilesystemResourceDirectory
  See https://dev.plone.org/ticket/13506
  [kroman0]

- Check appropriate permission for 'Revert to this revision' button.
  [danjacka]


2.3.4 (2013-03-05)
------------------

- handle missing feed type so it doesn't throw an error
  [vangheem]

- handle absense of ACTUAL_URL on request.
  Fixes https://dev.plone.org/ticket/13173
  [vangheem]

- Also show history on the folder contents view
  [vangheem]


2.3.3 (2013-01-01)
------------------

- Changed the behaviour of the title viewlet for items in the portal_factory.
  See https://dev.plone.org/ticket/12117
  [alert]

- Fix an edge case where getNavigationRootObject could loop infinitely.
  [davisagli]

- Add 'subsection' prefix to the all sections below to avoid classnames
  that start with digits, which is not permitted by the CSS standard.
  [erral]

- Display publication date only if Effective date is set, regardless of object
  state. Tickets:
  https://dev.plone.org/ticket/13045 and https://dev.plone.org/ticket/13046
  [vipod]


2.3.2 (2012-10-17)
------------------

- Add Language='all' as a keyword argument to avoid LinguaPlone deleting it when
  it patches the catalog
  [erral]

- Use context object's url to create the cache key instead of the portal_url.
  [erral]

- Avoid extra space at the end of icon alt attributes.
  [davisagli]

- Merge plip #12905 to provide more body classes
  [vangheem]

- adding user roles to body class, eg: userrole-anonymous, ...
  [garbas]

- Use normalized template name for body class since dots are not a good idea in classes
  [daftdog]

2.3.1 (2012-08-29)
------------------

- Icons accessibility improvement. Append mimetype name to img alt attribute
  [toutpt]


2.3 (2012-08-11)
----------------

- Change breadcrumb separator to / (slash character) for accessibility, and added SEO benefits.
  see https://dev.plone.org/ticket/12904
  [polyester]

- Add language atribute to presentation.pt for WCAG 2.0 compliance.
  See https://dev.plone.org/ticket/12902
  [rmatt, polyester]

- Display publication date in author byline:
  https://dev.plone.org/ticket/8699
  [vipod]

- Remove hard dependency on ATContentTypes.
  [davisagli]

- Correctly hand action URLs not ending / [phrearch]

- Removed obsolete 'define-macro' and 'define-slot' from viewlet page tempates.
  Fixes http://dev.plone.org/ticket/11541.
  [kleist]

- nextprevious/nextprevious.pt: Use "view/site_url" instead of deprecated "view/portal_url".
  Closes http://dev.plone.org/ticket/12720.
  [kleist]

- Translate alt attribute of image tag generated by icon
  [toutpt]


2.2.7 (2012-08-11)
------------------

- Change breadcrumb separator to / (slash character) for accessibility, and added SEO benefits.
  see https://dev.plone.org/ticket/12904
  [polyester]

- Add language atribute to presentation.pt for WCAG 2.0 compliance.
  See https://dev.plone.org/ticket/12902
  [rmatt, polyester]

- Remove hard dependency on ATContentTypes.
  [davisagli]

- Add body class for each part of url path. plip12905
  [vangheem]

2.2.6 (2012-04-15)
------------------

- Move .row and .cell styles from footer.pt to Sunburst main_template.
  Fixes https://dev.plone.org/ticket/12156
  [agnogueira]

- Add link targets for all action based links.  The target can be
  configured on a per-action basis.
  [rpatterson]


2.2.5 (2012-01-26)
------------------

- Slightly changed the whitespace in sitemap.xml.gz.
  [maurits]

- Use the link_target attribute (e.g. ``_target``) of user actions in
  the personal bar, if set.
  Fixes http://dev.plone.org/ticket/11609
  [maurits]

- Added a page as a not-js fallback for the user dropdown menu
  [giacomos]


2.2.4 (2011-12-03)
------------------

- Add the ability for the navtree strategy to suppliment the query.
  Fixes a problem where the listing of default pages in navigation
  trees could no longer be enabled.
  [rossp]


2.2.3 (2011-10-17)
------------------

- Make Keyword viewlet link to the new p.a.search view, as well as respect
  navigation root.
  Fixes http://dev.plone.org/plone/ticket/12231

- Added on body a class related to subsite.
  The class is named site-x where x is navigation root object id.
  [thomasdesvenain]

- Treat aliases to the ``(Default)`` view of a content type also as a
  view template (providing IViewView).
  Fixes http://dev.plone.org/plone/ticket/8198
  [maurits]

- Fix possible ZCML load order issue by explicitly loading CMF permissions.
  Fixes http://dev.plone.org/plone/ticket/11869
  [davisagli]

- Fix bug where getNavigationRootObject goes into infinite loop if context is
  None.
  Fixes http://dev.plone.org/plone/ticket/12186
  [anthonygerrard]


2.2.2 (2011-08-23)
------------------

- Accessibility: Added a title and alt tag to the logo.
  This fixes http://dev.plone.org/plone/ticket/11689
  [fulv]

- Switching 'Skip to navigation' to be linked to the global navigation instead
  of the navigation portlet.
  This fixes http://dev.plone.org/plone/ticket/11728
  [spliter]


2.2.1 - 2011-08-08
------------------

- Refactor getNavigationRoot to make it simpler, fixing issues when
  relativeRoot is specified.
  [gotcha]

- 'placeholder' attribute for the searchbox instead of the custom JS handling
  of the same functionality.
  [spliter]


2.2 - 2011-07-19
----------------

- Fixed validation of the personal bar for anonymous user.
  [spliter]

- Replaced obsolete in HTML5 <acronym> element with <abbr>.
  References http://dev.plone.org/plone/ticket/11300.
  [spliter]

- Set the search form to submit to @@search in order to use the new
  search results page.
  [elvix]

- Updated the BaseIcon to return its html tag when called.
  [elvix]

- Updated search link in <head> to link to @@search - updated search results
  view.
  [spliter]

- Updated searchbox.pt to be linked to updated search results view.
  [spliter]


2.1.9 - unreleased
------------------

- Switching 'Skip to navigation' to be linked to the global navigation instead
  of the navigation portlet.
  This fixes http://dev.plone.org/plone/ticket/11728
  [spliter]


2.1.8 - 2011-07-04
------------------

- Show 'Manage portlets' fallback viewlet for all ILocalPortletAssignables, not
  just ATContentTypes items. This fixes
  http://code.google.com/p/dexterity/issues/detail?id=183
  [davisagli]


2.1.7 - 2011-06-30
------------------

- Footer viewlet have all viewlet base API (site_url, navigation_root_url, etc).
  [thomasdesvenain]

- Make the bodyClass play more nice with ZopeViewPageTemplateFile.
  This fixes https://dev.plone.org/plone/ticket/11825
  [WouterVH]


2.1.6 - 2011-06-02
------------------

- Use getPhysicalPath instead of absolute_url_path to handle correctly
  virtual hosting.
  This fixes http://dev.plone.org/plone/ticket/8787
  [encolpe]


2.1.5 - 2011-05-12
------------------

- Page title and logo image title are related to navigation root.
  Refs http://dev.plone.org/plone/ticket/9175.
  Added navigation_root_title to portal_state view.
  [thomasdesvenain]

- Fix missing workflow history entry for content creation.
  Closes http://dev.plone.org/plone/ticket/11305.
  [rossp]

- Respect typesUseViewActionInListings in sitemap.xml.
  [elro]

- Use the parent url for default pages in sitemap.xml.
  [elro]

- Exclude types_not_searched from sitemap.xml.
  This fixes http://dev.plone.org/plone/ticket/7145
  [elro]

- Reduce whitespace in sitemap.xml.
  [elro]

- sitemap.xml.gz support for INavigationRoot.
  [elro]

- Add MANIFEST.in.
  [WouterVH]

- Make ``getNavigationRoot`` behave correctly in ``INavigationRoot``-folders
  where a ``relativeRoot`` is specified.
  This fixes https://dev.plone.org/plone/ticket/8787
  [WouterVH]


2.1.4 - 2011-04-03
------------------

- Make the body `section-` class based on the navigation root instead of the
  site root.
  [elro]

- Added navigation_root to plone_portal_state.
  [elro]


2.1.3 - 2011-03-02
------------------

- Fixed i18n of the "Log in to add comments" button. It was a regression
  since 2.0. This fixes http://dev.plone.org/plone/ticket/11525
  [vincentfretin]


2.1.2 - 2011-02-10
------------------

- Add div#content wrapper to @@contenthistorypopup. This is the only popup
  that has its own template, and it needs a #content id for xdv configurations
  like that of plone.org.
  [smcmahon]

- Enable managing portlets of default pages.
  This fixes http://dev.plone.org/plone/ticket/10672
  [fRiSi]


2.1.1 - 2011-02-04
------------------

- Do not show personaltools if there aren't any user actions.
  This fixes https://dev.plone.org/plone/ticket/11460
  [fRiSi]


2.1 - 2011-01-13
----------------

- Update test to check for ``login`` instead of ``login_form``.
  [elro]

- Remove login redirect alias. As of Plone 4.1 there is a login script.
  [elro]


2.0.10 - 2011-06-02
-------------------

- Use getPhysicalPath instead of absolute_url_path to handle correctly virtual
  hosting. This fixes http://dev.plone.org/plone/ticket/8787
  [encolpe]


2.0.9 - 2011-05-12
------------------

- Make getNavigationRoot behave correctly in INavigationRoot-folders where a
  relativeRoot is specified. This fixes http://dev.plone.org/plone/ticket/8787
  [WouterVH]


2.0.8 - 2011-04-01
------------------

- Enable managing portlets of default pages. This fixes
  http://dev.plone.org/plone/ticket/10672
  [fRiSi]


2.0.7 - 2011-02-25
------------------

- Fixed i18n of the "Log in to add comments" button. It was a regression since
  2.0. This fixes http://dev.plone.org/plone/ticket/11525
  [vincentfretin]


2.0.6 - 2011-01-03
------------------

- Depend on ``Products.CMFPlone`` instead of ``Plone``.
  [elro]

- Avoid creating persistent DiscussionItemContainers prematurely when items
  are viewed that have commenting enabled but no actual comments yet.
  [davisagli]

- Don't cache navigation_root_path and navigation_root_url contextless
  http://dev.plone.org/plone/ticket/11291
  [tom_gross]

- Add ids to links personal_bar when rendered as anonymous so they can be
  styled. This makes behavior consistent with the authenticated personal_bar.
  http://dev.plone.org/plone/ticket/10850
  [eleddy]


2.0.5 - 2010-11-15
------------------

- Fix presentation view when headings have HTML attributes (such as headings
  translated from reStructured Text). This fixes
  http://dev.plone.org/plone/ticket/10689
  [davisagli]

- Removed unnecessary memoization of the presentation view; turned its tests
  into unit tests.
  [davisagli]

- XHTML 1.0 Strict searchbox.pt.
  This fixes http://dev.plone.org/plone/ticket/11007
  [kiorky]


2.0.4 - 2010-09-28
------------------

- Fixed @@plone_context_state.view_template_id handling of content that does
  not implement IBrowserDefault (Products.CMFDynamicViewFTI). It was possible
  for this code to raise Unauthorized even when the user had permission to
  access the default view of the current context.
  [mj]

- Avoid conflict in selected tabs when the id of an excluded item starts with the
  same id of an existing tab.
  Fixes http://dev.plone.org/plone/ticket/11140
  [WouterVH]


2.0.3 - 2010-09-15
------------------

- Translate comment messages on history
  [tdesvenain]

- 'Compare' link is not available
  if content type is not registered in portal_diff.
  Fixes http://dev.plone.org/plone/ticket/11107.
  [tdesvenain]

- Added icons to related items viewlet for file types
  Fixes http://dev.plone.org/plone/ticket/10866
  [cwainwright]


2.0.2 - 2010-08-03
------------------

- Use "index" instead of "render" to ease customization of next/prev and rss
  viewlets.
  [esteele]

- Use unicode double arrows for next/previous links instead of right/left arrow
  images.
  [esteele]

- Correct CSS class attribute for next/previous links.
  [esteele]


2.0.1 - 2010-07-18
------------------

- Update license to GPL version 2 only.
  [hannosch]


2.0 - 2010-07-01
----------------

- Removed notice about registered trademark from the footer, that's what (R)
  means anyway.
  [limi]

- Make sure the presentation mode warning (if the document has no headings)
  displays properly. Fixes http://dev.plone.org/plone/ticket/10689.
  [davisagli]

- Adding "deactivated" class to menus by default, so they won't flicker on load.
  This fixes http://dev.plone.org/plone/ticket/10470.
  [limi]

- Determine whether to show the history link in the byline viewlet based on
  whether the user has the 'CMFEditions: Access previous versions'
  permission, rather than based on whether the user is anonymous or not.
  Fixes http://dev.plone.org/plone/ticket/10640.
  [davisagli]

- Add an 'icons-on' class to the body when icons are enabled, so that icons
  applied via CSS can also be controlled.
  [davisagli]


2.0b8 - 2010-06-03
------------------

- Only show the history link in the byline on the default view. This avoids
  having the links in folder listing views.
  [hannosch]

- The condition on the author link in the byline was reversed.
  [rossp]

- Document byline should not show history link to anonymous users.
  [elro]


2.0b7 - 2010-05-03
------------------

- Fixed personal_bar.pt to not repeat the UL tag for each user action.
  This fixes http://dev.plone.org/plone/ticket/10481
  [xMartin, dunlapm]

- Fixed CMFContentIcon to not return a url if the getIcon lookup fails
  in the same way that brain-based icons do. This fixes
  http://dev.plone.org/plone/ticket/10466
  [dunlapm]

- Cleaned up content history viewlets and overlays by eliminating
  superfluous div tags from the output.
  [dunlapm]

- Added apple-touch-icon (iPhone/iPad home screen icon) definition to
  favicon.pt
  [limi]


2.0b6 - 2010-04-07
------------------

- The catalog brains icon return no icon if the type's icon_expr is
  empty.
  [rossp]

- Extend the have_portlets check to make it possible to force a portlet column
  to be enabled even if there are no portlets.
  [davisagli]

- Simplified Related Items to use a definition list instead of a fieldset -
  it's really not a form.
  [limi]

- Change keyword/tag viewlet to be independent of the surrounding language,
  and to have a class on the separator, so it can be removed when the styling
  requires it.
  [limi]

- Update viewlets so that this package now defines the viewlet configuration
  required by the Sunburst theme, and plonetheme.classic overrides that to
  achieve the old viewlet positions.
  [davisagli]


2.0b5 - 2010-03-05
------------------

- Make icon descriptions' lookup of portal_type title less brittle for missing
  portal_types (fall back to the portal_type id).
  [davisagli]

- Further optimize the related_items view by avoiding an algorithm with
  quadratic complexity.
  [hannosch]


2.0b4 - 2010-02-18
------------------

- Updated history_view.pt to the recent markup conventions.
  References http://dev.plone.org/old/plone/ticket/9981
  [spliter]


2.0b3 - 2010-02-17
------------------

- Speed up related items viewlet by returning catalog brains instead of
  full objects.
  [stefan]

- Updated dashboard.pt to follow recent markup conventions.
  References http://dev.plone.org/old/plone/ticket/9981
  [spliter]

- Moved condition for .contentViews and .contentActions to div#edit-bar to not
  include #edit-bar in tabs should not be rendered.
  [spliter]

- Disabled columns in dashboard.pt with REQUEST variables according to the
  recent conventions.
  [spliter]

- Removing redundant .documentContent markup.
  This refs http://dev.plone.org/plone/ticket/10231.
  [limi]

- Moved the prepareObjectTabs method from the @@plone view to the contentviews
  viewlet and introduced a class for the viewlet.
  [hannosch]

- Introduce a new @@plone_layout globals view, which contains methods from the
  @@plone view and which were commonly overridden to change layout policies.
  [hannosch]

- Moved the history link back into the byline. This refs
  http://dev.plone.org/plone/ticket/10102.
  [hannosch]

- Add html id to personal bar actions.
  [paul_r]

- Created several modifications of the content history viewlet to act as
  standalone history page and simple popup. Old collapsible history viewlet
  is still in place, ready to be wired in with zcml for anyone who needs the
  old behavior.
  [smcmahon]

- Fixed broken reference to portal_workflow in document_relateditems-viewlet
  [tom_gross]


2.0b2 - 2010-01-31
------------------

- Use the same designation for "Plone" in the portal footer and the
  colophon.
  Fixes http://dev.plone.org/plone/ticket/9741.
  [dukebody]


2.0b1 - 2010-01-25
------------------

- Micro-optimization for skip_links viewlet.
  [hannosch]

- Update presentation fullscreen view to match current main_template's.
  [hannosch]

- Simplify the TAL of the dublin core viewlet.
  [hannosch]

- Avoid the overhead of a DateTime class in the footer.
  [hannosch]

- Optimized the related items viewlet.
  [hannosch]

- Avoid looking a "request/SearchableText|nothing" expression. Looking things
  up in the entire request which aren't there most of the time is actually
  somewhat slow.
  [hannosch]

- Optimized the content history viewlet.
  [hannosch]

- Optimize TAL code of the byline viewlet.
  [hannosch]

- Registered new viewlet for related items instead of using a macro.
  References http://dev.plone.org/plone/ticket/9985.
  [spliter]

- Always return an id to ensure searchbox viewlet produces valid HTML
  when livesearch is disabled.
  Fixes http://dev.plone.org/plone/ticket/9405 - thanks saily.
  [pelle]


2.0a5 - 2009-12-27
------------------

- Use the getIconExprObject method of the FTI instead of the deprecated
  getIcon method.
  [hannosch]

- Specified package dependencies.
  [hannosch]

- Use the correct ViewPageTemplateFile from Five for the links viewlets.
  [hannosch]


2.0a4 - 2009-12-16
------------------

- Do not let the homelink in the personal bar viewlet point to the
  author page but to the personalize_form (or dashboard).
  Fixes http://dev.plone.org/plone/ticket/8707
  [maurits]

- ``plone.htmlhead.title`` was not editable TTW. This closes
  http://dev.plone.org/plone/ticket/9488.
  [hannosch]


2.0a3 - 2009-12-02
------------------

- Properly placed path bar above the content.
  http://dev.plone.org/plone/ticket/9860
  [spliter]

- plone.manage_portlets_fallback viewlet's implementation
  http://dev.plone.org/plone/ticket/9808
  [spliter]

- Only show diff and revert buttons for most recent version if it
  differs from the working copy.
  http://dev.plone.org/plone/ticket/9803
  [alecm]

- Remove review_state from version history info, it's not always there
  and we weren't using it.
  http://dev.plone.org/plone/ticket/9816
  [alecm]

- Pass the creator id to /author/ as a parameter if it contains a '/', such
  as openid users.
  [matthewwilkes]

- Portal logo has to have 'title' attribute for better accessibility.
  [spliter]


2.0a2 - 2009-11-15
------------------

- Package metadata cleanup.
  [hannosch]

- Avoid calling lots of Python scripts from inside the content history viewlet
  and use methods on the view instead.
  [hannosch]


2.0a1 - 2009-11-15
------------------

- Moved plone.path_bar to the plone.abovecontenttitle viewlet
  manager, breadcrumbs should be close to the title of the current document.
  [limi]

- It's no longer the dashboard's responsibility to supply prefs/profile links
  now that they are located in the user menu.
  The code uses the "group" terminology here though, so I'm wondering if this is
  related to group dashboards. If I broke anything, let me know.
  [limi]

- Micro-optimize the icons views.
  [hannosch]

- Merged the ``selectedTabs`` Python script into the GlobalSectionsViewlet.
  [hannosch]

- Take advantage of icons being found on the actions themselves now instead
  and avoid the getIconFor indirection.
  [hannosch]

- Removed the special default page and translation handling. LinguaPlone uses
  a content language negotiator per default instead.
  [hannosch]

- Add a viewlet to display the Dublin Core metadata added in
  http://dev.plone.org/plone/ticket9272
  [esteele]

- Added support for group dashboards to the dashboard view.
  [optilude]

- Greatly simplify the default colophon, so it stands a chance of staying on
  actual sites. We cannot claim any standards support for public sites, only
  for Plone itself.
  [hannosch]

- Changed the is_rtl method of the portal state view not to rely on the locale
  but use a much simpler test based on the language code. This avoids setting
  up the expensive request.locale.
  [hannosch]

- Fixed the portal state view to look for uppercase language in the request,
  since that is set by PloneLanguageTool. This closes
  http://dev.plone.org/plone/ticket/8342.
  [hannosch]

- "Log in to add comments" button is now a link and respects the login URL
  specified in portal_actions. Closes http://dev.plone.org/plone/ticket/9071.
  [erikrose]

- Fixed is_rtl test to work with new locale based approach.
  [hannosch]

- Removed memoizing for things which are only used once in a page.
  [hannosch]

- Replaced direct invocations of interfaces with queryAdapter calls. The
  former does a suboptimal getattr call internally.
  [hannosch]

- Sanitized the actions handling on the context state view. You can pass in
  an action category into the action method now, which is the preferred way.
  This allows us to avoid evaluating all actions in the current context if
  we are only interested in some of the categories.
  [hannosch]

- Since Zope 2.11 the locale is available on the request. Removed our special
  code from the portal state view and rely directly on the request.
  [hannosch]

- Changed ViewletBase so viewlets can be registered as zope.contentproviders.
  This closes http://dev.plone.org/plone/ticket/7868.
  [hannosch]

- Purge old zope2 Interface interfaces for Zope 2.12 compatibility.
  [elro]


1.2.5 - 2009-08-01
------------------

- In the history viewlet, moved again the arrows inside a span, it's really needed to apply a style.
  [vincentfretin]


1.2.4 - 2009-07-04
------------------

- In the history viewlet, internationalized the Compare link and replaced
  icons by plain text. The revert link is now a POST button. This closes
  http://dev.plone.org/plone/ticket/9064
  [limi, vincentfretin]


1.2.3 - 2009-06-12
------------------

- Fix issue when dealing with empty version histories in history viewlet.
  [alecm]


1.2.2 - 2009-06-11
------------------

- Make ContentHistoryViewlet use new metadata only history method to
  speed up listing.
  [alecm]

- Make ContentHistoryViewlet check if context isVersionable.
  [elro]


1.2.1 - 2009-05-20
------------------

- Changed the search and author header links to respect the navigation root.
  [hannosch]


1.2 - 2009-05-16
----------------

- Filter not-interesting history entries in content history viewlet. This
  prevents an empty history viewlet from being shown.
  [wichert]

- Add a new content history viewlet which combines the full workflow history
  and content versions. Render this instead of the workflow history viewlet.
  [wichert]

- Fixed querystring in CSS validation link in viewlets/colophon.pt
  There was an ampersand where the leading "?" should have been.
  http://dev.plone.org/plone/ticket/9054
  [siebo]

- Fixed "region-content" id twice in dashboard.pt, replaced one by "content".
  Fixes http://dev.plone.org/plone/ticket/8932
  [vincentfretin]

- Author link tag should follow same rules as byline viewlet.
  [elro]


1.2rc1 - 2009-03-20
-------------------

- Fixed i18n in content_history template.
  There were two nested msgids and dynamic content.
  [vincentfretin]

- Removed stray span tags in the comment byline.
  [limi]


1.2b1 - 2009-03-07
------------------

- Added navigation_root_url to the common viewlets base class. Adjusted the
  various viewlets templates to use the new attribute. Changed the dashboard
  view to be available on an INavigationRoot.
  This implements http://plone.org/products/plone/roadmap/234
  [calvinhp]

- Default to using the content history viewlet instead of the workflow history
  viewlet.
  [wichert]

- Add options to show differences between consecutive versions, and revert to
  and preview older revisions to the content history viewlet.
  [wichert]

- Use the new history view from CMFEditions instead of the crufty old form.
  [wichert]


1.1.8 - 2009-03-07
------------------

- Adjust the caching of sitemap.xml.gz. We only cache for anonymous users. That
  fixes a bug where a cached sitemap.xml.gz is delivered with information that
  only an user with more privilegs is allowed to see. We also make sure that
  the cached file was build with a current catalog by adding the catalog
  counter to the cache key. Based on a patch by stxnext.  Fixes
  http://dev.plone.org/plone/ticket/8402
  [stxnext, csenger]

- Added time_only for use with toLocalizedTime so that event_view now localizes
  the start/end times if the start/end dates are the same. Closes
  http://dev.plone.org/plone/ticket/8607
  [jnelson, calvinhp]

- Fixed Plone 3.1 backward compatibility of above.
  [stefan]


1.1.7 - 2008-12-15
------------------

- Modified user profile item on the dashboard to use an image tag
  instead of a background image. This makes it more consistent with
  the other list items and easier to style for RTL scripts.
  [emanlove]


1.1.6 - 2008-11-21
------------------

- Avoid a test failure caused by test interdependencies.
  [hannosch]

- Fixed tests for the language method of the portal state view.
  [hannosch]

- Fixed keywords.pt to properly encode ampersands in its links. This closes
  http://dev.plone.org/plone/ticket/8509
  [younga3, dunlapm]

- Fixed site_icon so that we would have flipped icon in case of RTL.
  This closes http://dev.plone.org/plone/ticket/4576
  [spliter]

- Fixed generation of links to author.cpt for user IDs that are a URL
  (OpenID users, e.g.).  This closes http://dev.plone.org/plone/ticket/8040
  [davisagli]

- Add some tests on private contents for sitemap.xml.gz generation.  This
  closes http://dev.plone.org/plone/ticket/8402
  [encolpe]


1.1.5 - 2008-08-18
------------------

- Fixed an invalid message id for the dashboard. This closes
  http://dev.plone.org/plone/ticket/7758.
  [hannosch]

- Fixed comments.pt to pass the title of the comment you are replying to into
  the discussion_reply_form. This closes
  http://dev.plone.org/plone/ticket/8323
  [calvinhp]

- Refactor default_page: move all logic out of the view to separate methods
  so they can be called without a request (which is not used at all).
  Deprecate parameters which were not in the interface and were never used.
  [wichert]

- Added note that Javascript is required for presentation mode. This closes
  http://dev.plone.org/plone/ticket/7575 and
  http://dev.plone.org/plone/ticket/7573
  [limi]

- Fixed plone_context_state's view_url method to work with contexts that don't
  have a portal_type.  This closes http://dev.plone.org/plone/ticket/8028.
  [davisagli]

- Changed IContentIcon to expose users to the title of the FTI instead of the
  portal_type. This closes http://dev.plone.org/plone/ticket/8246.
  [hannosch]

- Adjusted deprecation warnings to point to Plone 4.0 instead of Plone 3.5
  since we changed the version numbering again.
  [hannosch]


1.1.3 - 2008-07-07
------------------

- Made PersonalBarViewlet tolerate users who don't have a Plone user object, as
  when using OpenID or apachepas. This fixes
  http://dev.plone.org/plone/ticket/7296.
  [erikrose]

- Use 'index' attribute rather than 'render' for setting viewlet templates, so
  that they can be overridden using the 'template' ZCML attribute.
  [davisagli]


1.1.0 - 2008-04-20
------------------

- Applied patch from http://dev.plone.org/plone/ticket/7942 to ensure that the
  'currentParent' marker is not True for items that have a path that is a
  substring of the true path.
  [optilude]

- Displaying 'Anonymous User' also when the comment creator is an empty
  string. This fixes http://dev.plone.org/plone/ticket/7712.
  [rsantos]

- Allow the use of the icon attribute on action directly instead of using the
  actionicons tool.
  [hannosch]

- Fix invalid leading space in all 'Up to Site Setup' links.
  [wichert]

- Fixed permission in workflow history viewlet. This closes
  http://dev.plone.org/plone/ticket/5507.
  [hannosch]

- Made handling of self.context in portal.py consistent.
  [hannosch]

- Rename the portal_url instance variable to site_url in the ViewletBase
  class. This prevents getToolByName(..., 'portal_url') from returning
  the URL string instead of the portal_url tool, which can causes unexpected
  and subtle breakage. portal_url is still available but produces a deprecation
  warning. It will be removed in Plone 4.
  [wichert]

- Added viewlet for RSS link.
  [fschulze]

- Added dependency on plone.app.viewletmanager.
  [fschulze]

- Make viewlet managers in head section order- and filterable.
  [fschulze]


1.0.6 - 2008-09-10
------------------

- Added i18n markup to nextprevious.pt.
  This closes http://dev.plone.org/plone/ticket/7537.
  [hannosch]

- Catch KeyError for presentation or tableContents when document
  has an out-of-date schema.  Can happen when migrating from Plone
  2.5 to 3.0. Fall back to False for those attributes then.
  [maurits]


1.0.5 - 2008-01-03
------------------

- Do not create an empty <ul> in the personal actions bar if there are
  no items in it. This fixes an XHTML syntax error.
  [wichert]


1.0.4 - 2007-12-06
------------------

- Added i18n domain to comment.pt.
  [martior]

- Allow non ascii characters in webstats_js code.
  Fixes http://dev.plone.org/plone/ticket/7359
  [naro]

- Fixed workflow history viewlet to handle entries with
  usernames that don't exist any more (deleted users) and
  also anonymous users.
  This fixes http://dev.plone.org/plone/ticket/7250.
  [rsantos]


1.0.3 - 2007-11-09
------------------

- Made getIcon urls relative to portal root.
  [tesdal]


1.0.2 - 2007-10-08
------------------

- Fixed getIcon code for use with ++resource++ and to use a safer method
  of getting the correct url.
  [optilude]

- Upgraded the sitemap template to conform with the 0.9 specs from
  http://www.sitemaps.org and fixed the caching to use the filename.
  [deo]


1.0.1.1 - 2007-09-10
--------------------

- Lower logging level of 'no associated workflow' to avoid a log entry
  on each view.
  [ldr]

- Fixed default language in globals.
  [wichert]

- Fixed link to actor in history viewlet.
  [naro]

- Avoid locking on non lockable types in byline viewlet.
  [jfroche]

- Added website statistics inclusion viewlet to configure.zcml so it
  actually works.
  [fschulze]

- Made code in defaultpage.py a bit more tolerant of missing tools.
  [hannosch]


1.0 - 2007-08-17
----------------

- Fixed the translation of the 'Show this page in presentation mode...'
  message.
  [hannosch]

- Made the search box a bit wider, so the entire default text is shown
  in languages with a rather long term.
  [hannosch]

- Show the authors full name in presentation view. This fixes
  http://dev.plone.org/plone/ticket/6810
  [wichert]

.. _`CMFPlone#741`: https://github.com/plone/Products.CMFPlone/issues/741
.. _`CMFPlone#1000`: https://github.com/plone/Products.CMFPlone/issues/1000
.. _`CMFPlone#1037`: https://github.com/plone/Products.CMFPlone/issues/1037
.. _`CMFPlone#1151`: https://github.com/plone/Products.CMFPlone/issues/1151
.. _`CMFPlone#1178`: https://github.com/plone/Products.CMFPlone/issues/1178
.. _`CMFPlone#1556`: https://github.com/plone/Products.CMFPlone/issues/1556
