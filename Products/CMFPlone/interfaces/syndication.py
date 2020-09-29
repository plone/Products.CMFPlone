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
        title=_('Allowed'),
        description=_('Allow syndication for collections and folders '
                      'on site.'),
        default=True)

    default_enabled = schema.Bool(
        title=_('Enabled by default'),
        description=_('If syndication should be enabled by default for all '
                      'folders and collections.'),
        default=False)

    search_rss_enabled = schema.Bool(
        title=_('Search RSS enabled'),
        description=_('Allows users to subscribe to feeds of search results'),
        default=True)

    show_author_info = schema.Bool(
        title=_('Show author info'),
        description=_('Should feeds include author information'),
        default=True)

    render_body = schema.Bool(
        title=_('Render Body'),
        description=_('help_render_body',
                      default='If body text available for item, '
                      'render it, otherwise use description.'),
        default=False)

    max_items = schema.Int(
        title=_('label_syndication_max_items',
                default='Maximum items'),
        description=_('help_syndication_max_items',
                      default='Maximum number of items that will be syndicated.'),
        min=1,
        default=15)

    allowed_feed_types = schema.Tuple(
        title=_('Allowed Feed Types'),
        description=_("Separate view name and title by '|'"),
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
        title=_('Site RSS'),
        description=_('Paths to folders and collections to link to '
                      'at the portal root.'),
        required=False,
        default=('/news/aggregator',),
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.SyndicatableFeedItems")
    )

    show_syndication_button = schema.Bool(
        title=_("Show settings button"),
        description=_("Makes it possible to customize syndication settings "
                      "for particular folders and collections "))

    show_syndication_link = schema.Bool(
        title=_("Show feed link"),
        description=_("Enable RSS link document action on the syndication "
                      "content item."))


class IFeedSettings(Interface):

    enabled = schema.Bool(
        title=_('Enabled'),
        default=False)

    feed_types = schema.Tuple(
        title=_('Feed Types'),
        required=True,
        missing_value=None,
        default=("RSS", "rss.xml", "atom.xml"),
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.SyndicationFeedTypes"
        ))

    render_body = schema.Bool(
        title=_('Render Body'),
        description=_(
            'help_render_body',
            default='If body text available for item, '
                    'render it, otherwise use description.'),
        default=False)

    max_items = schema.Int(
        title=_('label_syndication_max_items',
                default='Maximum items'),
        description=_(
            'help_syndication_max_items',
            default='Maximum number of items that will be syndicated.'),
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
