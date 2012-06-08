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
        default=True)

    search_rss_enabled = schema.Bool(
        title=_(u'Search RSS enabled'),
        default=True)

    show_author_info = schema.Bool(
        title=_(u'Show author info'),
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


class IFeedSettings(Interface):

    enabled = schema.Bool(title=_(u'Enabled'))

    feed_types = schema.Tuple(
        title=_(u'Feed Types'),
        required=True,
        missing_value=None,
        default=("rss.xml", "atom.xml"),
        value_type=schema.Choice(
            # XXX Should be registry configurable
            vocabulary=SimpleVocabulary([
                SimpleTerm(value='rss.xml', token='rss.xml',
                    title=_(u'RSS 2.0')),
                SimpleTerm(value='atom.xml', token='atom.xml',
                    title=_(u'Atom')),
                SimpleTerm(value='itunes.xml', token='itunes.xml',
                    title=_(u'iTunes')),
            ])
        ))

    render_body = schema.Bool(
        title=_(u'Render Body'),
        description=_(u'help_render_body',
                default=u'If body text available for item, '
                        u'render it, otherwise use description.'),
        default=False)

    media_feed = schema.Bool(
        title=_(u'Media Feed'),
        description=_(u'help_media_feed',
                default=u'If you want to support media files with enclosures '
                        u'if your feed.'),
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

    def adapter():
        """
        get the feed adapter
        """

    def context_allowed():
        """
        if syndication is enabled on the context
        """

    def context_enabled():
        """
        """

    def site_enabled():
        """
        """

    def search_rss_enabled():
        """
        """

    def show_author_info():
        """
        """

    def allowed_feed_types():
        """
        """

    def search_adapter():
        """
        """
    
