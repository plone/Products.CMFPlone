from zope.component import adapts
from zope.interface import implements
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from Products.CMFPlone.interfaces.syndication import ISyndicatable
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from Products.CMFPlone.interfaces.syndication import ISiteSyndicationSettings
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

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

        registry = getUtility(IRegistry)
        self.site_settings = registry.forInterface(ISiteSyndicationSettings,
                                                   check=False)

    def __setattr__(self, name, value):
        if name in ('context', '_metadata', 'site_settings'):
            self.__dict__[name] = value
        else:
            self._metadata[name] = value

    def __getattr__(self, name):
        default = None
        if name in ISiteSyndicationSettings.names():
            default = getattr(self.site_settings, name)
        elif name == 'enabled' and self.site_settings.default_enabled:
            default = True
        elif name in IFeedSettings.names():
            default = IFeedSettings[name].default

        return self._metadata.get(name, default)
