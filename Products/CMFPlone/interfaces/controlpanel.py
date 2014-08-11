from Products.CMFPlone import PloneMessageFactory as _
from basetool import IPloneBaseTool
from plone.locking.interfaces import ILockSettings
from zope.interface import Attribute
from zope.interface import Interface
from zope import schema


class IControlPanel(IPloneBaseTool):
    """ Interface for the ControlPanel """

    def registerConfiglet(id, name, action, condition='', permission='',
                          category='Plone', visible=1, appId=None,
                          imageUrl=None, description='', REQUEST=None):
        """ Registration of a Configlet """

    def unregisterConfiglet(id):
        """ unregister Configlet """

    def unregisterApplication(appId):
        """ unregister Application with all configlets """

    def getGroupIds():
        """ list of the group ids """

    def getGroups():
        """ list of groups as dicts with id and title """

    def enumConfiglets(group=None):
        """ lists the Configlets of a group, returns them as dicts by
            calling .getAction() on each of them """


class IEditingSchema(Interface):

    visible_ids = schema.Bool(
        title=_(u"Show 'Short Name' on content?"),
        description=_(
            u"Display and allow users to edit the "
            u"'Short name' content identifiers, which form the "
            u"URL part of a content item's address. Once "
            u"enabled, users will then be able to enable this "
            u"option in their preferences."),
        default=False,
        required=False)

    default_editor = schema.Choice(
        title=_(u'Default editor'),
        description=_(
            u"Select the default wysiwyg "
            u"editor. Users will be able to choose their "
            u"own or select to use the site default."),
        default=u'TinyMCE',
        missing_value=set(),
        vocabulary="plone.app.vocabularies.AvailableEditors",
        required=True)

    ext_editor = schema.Bool(
        title=_(u'Enable External Editor feature'),
        description=_(
            u"Determines if the external editor "
            u"feature is enabled. This feature requires a "
            u"special client-side application installed. The "
            u"users also have to enable this in their "
            u"preferences."),
        default=False,
        required=False)

    enable_link_integrity_checks = schema.Bool(
        title=_(u"Enable link integrity checks"),
        description=_(
            u"Determines if the users should get "
            u"warnings when they delete or move content that "
            u"is linked from inside the site."),
        default=True,
        required=False)

    lock_on_ttw_edit = schema.Bool(
        title=_(u"Enable locking for through-the-web edits"),
        description=_(
            u"Disabling locking here will only "
            u"affect users editing content through the "
            u"Plone web UI.  Content edited via WebDAV "
            u"clients will still be subject to locking."),
        default=True,
        required=False)


class IMaintenanceSchema(Interface):

    days = schema.Int(
        title=_(u"Days of object history to keep after packing"),
        description=_(
            u"You should pack your database regularly. This number "
            u"indicates how many days of undo history you want to "
            u"keep. It is unrelated to versioning, so even if you "
            u"pack the database, the history of the content changes "
            u"will be kept. Recommended value is 7 days."
        ),
        default=7,
        required=True
    )


class INavigationSchema(Interface):

    generate_tabs = schema.Bool(
        title=_(u"Automatically generate tabs"),
        description=_(
            u"By default, all items created at the root level will " +
            u"add to the global section navigation. You can turn this off " +
            u"if you prefer manually constructing this part of the " +
            u"navigation."),
        default=True,
        required=False)

    nonfolderish_tabs = schema.Bool(
        title=_(u"Generate tabs for items other than folders."),
        description=_(
            u"By default, any content item in the root of the portal will" +
            u"be shown as a global section. If you turn this option off, " +
            u"only folders will be shown. This only has an effect if " +
            u"'Automatically generate tabs' is enabled."),
        default=True,
        required=False)

    displayed_types = schema.Tuple(
        title=_(u"Displayed content types"),
        description=_(
            u"The content types that should be shown in the navigation and " +
            u"site map."),
        required=False,
        default=('Image', 'File', 'Link', 'News Item', 'Folder', 'Document', 'Event'),
        value_type=schema.Choice(
            source="plone.app.vocabularies.ReallyUserFriendlyTypes"
        ))

    filter_on_workflow = schema.Bool(
        title=_(u"Filter on workflow state"),
        description=_(
            u"The workflow states that should be shown in the navigation " +
            u"tree and the site map."),
        default=False,
        required=False)

    workflow_states_to_show = schema.Tuple(
        required=False,
        default=(),
        value_type=schema.Choice(
            source="plone.app.vocabularies.WorkflowStates"))

    show_excluded_items = schema.Bool(
        title=_(
            u"Show items normally excluded from navigation if viewing their " +
            u"children."),
        description=_(
            u"If an item has been excluded from navigation should it be " +
            u"shown in navigation when viewing content contained within it " +
            u"or within a subfolder."),
        default=True,
        required=False)


class ISearchSchema(Interface):

    enable_livesearch = schema.Bool(
        title=_(u'Enable LiveSearch'),
        description=_(
            u"Enables the LiveSearch feature, which shows live "
            u"results if the browser supports JavaScript."),
        default=True,
        required=True
    )

    types_not_searched = schema.Tuple(
        title=_(u"Define the types to be shown in the site and searched"),
        description=_(
            u"Define the types that should be searched and be "
            u"available in the user facing part of the site. "
            u"Note that if new content types are installed, they "
            u"will be enabled by default unless explicitly turned "
            u"off here or by the relevant installer."
        ),
        required=False,
        default=(
            'ATBooleanCriterion',
            'ATDateCriteria',
            'ATDateRangeCriterion',
            'ATListCriterion',
            'ATPortalTypeCriterion',
            'ATReferenceCriterion',
            'ATSelectionCriterion',
            'ATSimpleIntCriterion',
            'ATSimpleStringCriterion',
            'ATSortCriterion',
            'ChangeSet',
            'Discussion Item',
            'Plone Site',
            'TempFolder',
            'ATCurrentAuthorCriterion',
            'ATPathCriterion',
            'ATRelativePathCriterion',
        ),
        value_type=schema.Choice(
            source="plone.app.vocabularies.PortalTypes"
        ),
    )


class ISiteSchema(ILockSettings):

    site_title = schema.TextLine(
        title=_(u'Site title'),
        description=_(
            u"This shows up in the title bar of "
            u"browsers and in syndication feeds."),
        default=u'Plone site')

    exposeDCMetaTags = schema.Bool(
        title=_(u"Expose Dublin Core metadata"),
        description=_(u"Exposes the Dublin Core properties as metatags."),
        default=False,
        required=False)

    enable_sitemap = schema.Bool(
        title=_(u"Expose sitemap.xml.gz"),
        description=_(
            u"Exposes your content as a file "
            u"according to the sitemaps.org standard. You "
            u"can submit this to compliant search engines "
            u"like Google, Yahoo and Microsoft. It allows "
            u"these search engines to more intelligently "
            u"crawl your site."),
        default=False,
        required=False)

    webstats_js = schema.SourceText(
        title=_(u'JavaScript for web statistics support'),
        description=_(
            u"For enabling web statistics support "
            u"from external providers (for e.g. Google "
            u"Analytics). Paste the code snippets provided. "
            u"It will be included in the rendered HTML as "
            u"entered near the end of the page."),
        default=u'',
        required=False)


class IDateAndTimeSchema(Interface):
    """Controlpanel settings for date and time related settings.
    """

    portal_timezone = schema.Choice(
        title=_(u"Portal default timezone"),
        description=_(
            u"help_portal_timezone",
            default=u"The timezone setting of the portal. Users can set "
                    u"their own timezone, if available timezones are "
                    u"defined."),
        required=True,
        default=None,
        vocabulary="plone.app.vocabularies.CommonTimezones")

    available_timezones = schema.List(
        title=_(u"Available timezones"),
        description=_(
            u"help_available_timezones",
            default=u"The timezones, which should be available for the "
                    u"portal. Can be set for users and events"),
        required=False,
        default=[],
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.Timezones"))

    first_weekday = schema.Choice(
        title=_(u'label_first_weekday', default=u'First Weekday'),
        description=_(
            u'help_first_weekday',
            default=u'First day in the Week.'),
        required=True,
        default=None,
        vocabulary="plone.app.vocabularies.Weekdays")

class IMarkupSchema(Interface):

    default_type = schema.Choice(
        title=_(u'Default format'),
        description=_(
            u"Select the default format of textfields for newly "
            u"created content objects."
        ),
        default=u'text/html',
        vocabulary="plone.app.vocabularies.AllowableContentTypes",
        required=True
    )

    allowed_types = schema.Tuple(
        title=_(u'Alternative formats'),
        description=_(
            u"Select which formats are available for users as "
            u"alternative to the default format. Note that if new "
            u"formats are installed, they will be enabled for text "
            u"fields by default unless explicitly turned off here "
            u"or by the relevant installer."
        ),
        required=True,
        default=('text/html', 'text/x-web-textile'),
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.AllowableContentTypes"
        )
    )

class ITypesSchema(Interface):
    """
    """
