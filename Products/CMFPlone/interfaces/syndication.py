from zope.interface import Interface
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from Products.CMFPlone import PloneMessageFactory as _
from OFS.interfaces import IItem


class ISyndicatable(Interface):
    pass


class IFeeds(IItem):
    pass


class IFeed(Interface):
    """
    An adapter on the context and request
    to get feed information
    """
    def author(self):
        pass

    def title(self):
        pass

    def description(self):
        pass

    def image():
        pass

    def _items(self):
        """
        returns items for feed
        """


class ISearchFeed(IFeed):
    pass


class IFeedItem(Interface):
    """
    An adapter on the feed item and IFeed instance
    """


class ISiteSyndicationSettings(Interface):

    enabled = schema.Bool(
        title=_(u'Enabled'),
        description=_(u'Globally enabled for the site'),
        default=True)

    search_rss_enabled = schema.Bool(
        title=_(u'Search RSS enabled'),
        description=_(u'If the search_rss is enabled'),
        default=True)

    show_author_info = schema.Bool(
        title=_(u'Show author info'),
        description=_(u'Should feeds include author information'),
        default=True)

    update_period = schema.Choice(
        title=_(u'label_syndication_updateperiod',
                default=u'Update Period'),
        description=_(u'help_syndication_update_period',
                default=u'Controls how often the channel is updated.'),
        vocabulary=SimpleVocabulary([
            SimpleTerm(value='hourly', token='hourly', title=_(u'hourly')),
            SimpleTerm(value='daily', token='daily', title=_(u'daily')),
            SimpleTerm(value='weekly', token='weekly', title=_(u'weekly')),
            SimpleTerm(value='monthly', token='monthly', title=_(u'monthly'))
        ]),
        default=u'hourly')

    update_frequency = schema.Int(
        title=_(u'label_syndication_update_frequency',
                default=u'Update Frequency'),
        description=_(u'help_syndication_update_frequency',
                default=u"Controls the frequency of the updates. For example,"
                        u"if you want it to update twice a week,"
                        u'select "weekly" above, and "2" here.'),
        default=1)

    update_base = schema.Datetime(
        title=_(u'label_syndication_update_base',
                default=u'Update Base'),
        description=_(u'help_syndication_update_base',
                default=u'This is the date the updater starts counting from.'
                        u'So if you want to update weekly every Tuesday,'
                        u'make sure this starts on a Tuesday.'),
        required=False)

    max_items = schema.Int(
        title=_(u'label_syndication_max_items',
                default=u'Maximum Items'),
        description=_(u'help_syndication_max_items',
                default=u'Maximum number of items that will be syndicated.'),
        default=15)

    allowed_feed_types = schema.Tuple(
        title=_(u'Allowed Feed Types'),
        description=_(u'Seprate view name and title by "|"'),
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
        title=_(u"Show Settings Button"),
        description=_(u"To easily modify syndication settings on "
                      u"folders an collections"))

    show_syndication_link = schema.Bool(
        title=_(u"Show Feed Link"),
        description=_(u"Should the link to the feed be displayed."))


class IFeedSettings(Interface):

    enabled = schema.Bool(title=_(u'Enabled'))

    feed_types = schema.Tuple(
        title=_(u'Feed Types'),
        required=True,
        missing_value=None,
        default=("rss.xml", "atom.xml"),
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.SyndicationFeedTypes"
        ))

    render_body = schema.Bool(
        title=_(u'Render Body'),
        description=_(u'help_render_body',
                default=u'If body text available for item, '
                        u'render it, otherwise use description.'),
        default=False)

    update_period = schema.Choice(
        title=_(u'label_syndication_updateperiod',
                default=u'Update Period'),
        description=_(u'help_syndication_update_period',
                default=u'Controls how often the channel is updated.'),
        vocabulary=SimpleVocabulary([
            SimpleTerm(value='hourly', token='hourly', title=_(u'hourly')),
            SimpleTerm(value='daily', token='daily', title=_(u'daily')),
            SimpleTerm(value='weekly', token='weekly', title=_(u'weekly')),
            SimpleTerm(value='monthly', token='monthly', title=_(u'monthly'))
        ]),
        default=u'hourly')

    update_frequency = schema.Int(
        title=_(u'label_syndication_update_frequency',
                default=u'Update Frequency'),
        description=_(u'help_syndication_update_frequency',
                default=u"Controls the frequency of the updates. For example,"
                        u"if you want it to update twice a week,"
                        u'select "weekly" above, and "2" here.'),
        default=1)

    update_base = schema.Datetime(
        title=_(u'label_syndication_update_base',
                default=u'Update Base'),
        description=_(u'help_syndication_update_base',
                default=u'This is the date the updater starts counting from.'
                        u'So if you want to update weekly every Tuesday,'
                        u'make sure this starts on a Tuesday.'),
        required=False)

    max_items = schema.Int(
        title=_(u'label_syndication_max_items',
                default=u'Maximum Items'),
        description=_(u'help_syndication_max_items',
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
