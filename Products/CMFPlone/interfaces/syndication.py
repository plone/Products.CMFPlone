from zope.interface import Interface
from zope import schema
from Products.CMFPlone import PloneMessageFactory as _


class ISyndicatable(Interface):
    pass


class IFeedData(Interface):
    def link():
        """
        Link to item
        """

    def base_url():
        """
        base url to item
        """

    def title():
        """
        title of item
        """

    def description():
        """
        """

    def categories():
        """
        List of tags
        """

    def published():
        """
        publishing date
        """

    def modified():
        """
        modification date
        """

    def uid():
        """
        """

    def rights():
        """
        """

    def publisher():
        """
        """

    def author():
        """
        """

    def author_name():
        """
        """

    def author_email():
        """
        """


class IFeed(IFeedData):
    """
    An adapter on the context and request
    to get feed information
    """
    def show_about():
        """
        """

    def logo():
        """
        """

    def icon():
        """
        """

    def _brains():
        """
        return list of brains
        """

    def _items():
        """
        return full objects
        """

    def items():
        """
        adapted items
        """

    def limit():
        """
        """

    def language():
        """
        """


class ISearchFeed(IFeed):
    pass


class IFeedItem(IFeedData):
    """
    An adapter on the feed item and IFeed instance
    """

    def body():
        """
        """

    def guid():
        """
        """

    def has_enclosure():
        """
        """

    def file():
        """
        """

    def file_url():
        """
        """

    def file_length():
        """
        """

    def file_type():
        """
        """


class ISiteSyndicationSettings(Interface):

    allowed = schema.Bool(
        title=_(u'Allowed'),
        description=_(u'Allow syndication for collections and folders '
                      u'on site.'),
        default=True)

    default_enabled = schema.Bool(
        title=_(u'Enabled by default'),
        description=_(u'If syndication should be enabled by default for all '
                      u'folders and collections.'),
        default=False)

    search_rss_enabled = schema.Bool(
        title=_(u'Search RSS enabled'),
        description=_(u'Allows users to subscribe to feeds of search results'),
        default=True)

    show_author_info = schema.Bool(
        title=_(u'Show author info'),
        description=_(u'Should feeds include author information'),
        default=True)

    render_body = schema.Bool(
        title=_(u'Render Body'),
        description=_(u'help_render_body',
                      default=u'If body text available for item, '
                      u'render it, otherwise use description.'),
        default=False)

    max_items = schema.Int(
        title=_(u'label_syndication_max_items',
                default=u'Maximum items'),
        description=_(u'help_syndication_max_items',
                      default=u'Maximum number of items that will be syndicated.'),
        min=1,
        default=15)

    allowed_feed_types = schema.Tuple(
        title=_(u'Allowed Feed Types'),
        description=_(u"Separate view name and title by '|'"),
        required=True,
        missing_value=None,
        default=(
            "RSS|RSS 1.0",
            "rss.xml|RSS 2.0",
            "atom.xml|Atom",
            "itunes.xml|iTunes"),
        value_type=schema.TextLine()
    )

    site_rss_items = schema.Tuple(
        title=_(u'Site RSS'),
        description=_(u'Paths to folders and collections to link to '
                      u'at the portal root.'),
        required=False,
        default=('/news/aggregator',),
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.SyndicatableFeedItems")
    )

    show_syndication_button = schema.Bool(
        title=_(u"Show settings button"),
        description=_(u"Makes it possible to customize syndication settings "
                      u"for particular folders and collections "))

    show_syndication_link = schema.Bool(
        title=_(u"Show feed link"),
        description=_(u"Enable RSS link document action on the syndication "
                      u"content item."))


class IFeedSettings(Interface):

    enabled = schema.Bool(
        title=_(u'Enabled'),
        default=False)

    feed_types = schema.Tuple(
        title=_(u'Feed Types'),
        required=True,
        missing_value=None,
        default=("RSS", "rss.xml", "atom.xml"),
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.SyndicationFeedTypes"
        ))

    render_body = schema.Bool(
        title=_(u'Render Body'),
        description=_(
            u'help_render_body',
            default=u'If body text available for item, '
                    u'render it, otherwise use description.'),
        default=False)

    max_items = schema.Int(
        title=_(u'label_syndication_max_items',
                default=u'Maximum items'),
        description=_(
            u'help_syndication_max_items',
            default=u'Maximum number of items that will be syndicated.'),
        default=15)


class ISyndicationUtil(Interface):

    def allowed_feed_types():
        """
        get a list of allow feed types
        """

    def context_allowed():
        """
        If syndication is allowed on the context
        """

    def context_enabled(raise404=False):
        """
        If syndication is enabled on the context
        """

    def site_enabled():
        """
        If syndication is enabled on the site
        """

    def search_rss_enabled(raise404=False):
        """
        If search_rss is enabled
        """

    def show_author_info():
        """
        If author information should show on feeds
        """

    def max_items():
        """
        Default max items to show on the site
        """

    def rss_url():
        """
        Default rss url. Mainly to be used for the
        rss portal_action link
        """
