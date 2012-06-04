from zope.component import adapts
from zope.interface import implements
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from Products.CMFPlone.interfaces.syndication import ISyndicatable
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

FEED_SETTINGS_KEY = 'syndication_settings'


class FeedSettings(object):
    implements(IFeedSettings)
    adapts(ISyndicatable)

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)

        self._metadata = annotations.get(FEED_SETTINGS_KEY, None)
        if self._metadata is None:
            self._metadata = PersistentDict()
            annotations[FEED_SETTINGS_KEY] = self._metadata

    def __setattr__(self, name, value):
        if name in ('context', '_metadata'):
            self.__dict__[name] = value
        else:
            self._metadata[name] = value

    def __getattr__(self, name):
        default = None

        if name in IFeedSettings.names():
            default = IFeedSettings[name].default

        return self._metadata.get(name, default)


class SearchSettings(object):
    implements(IFeedSettings)
    adapts(IPloneSiteRoot)

    def __init__(self, context):
        self.render_body = True
        # XXX Need to get actual site settings!
        self.max_items = 15
