from persistent.dict import PersistentDict
from plone.base.interfaces.syndication import IFeedSettings
from plone.base.interfaces.syndication import ISiteSyndicationSettings
from plone.base.interfaces.syndication import ISyndicatable
from plone.registry.interfaces import IRegistry
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer


FEED_SETTINGS_KEY = "syndication_settings"


@adapter(ISyndicatable)
@implementer(IFeedSettings)
class FeedSettings:
    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(context)
        self.needs_saving = False

        self._metadata = self.annotations.get(FEED_SETTINGS_KEY, None)
        if self._metadata is None:
            self._metadata = PersistentDict()
            self.needs_saving = True

        registry = getUtility(IRegistry)
        self.site_settings = registry.forInterface(
            ISiteSyndicationSettings, check=False
        )

    def _set(self):
        """
        what are we doing here you might ask?
        well, this causes us to write on read so only set on annotation
        if we need to
        """
        if self.needs_saving:
            self.annotations[FEED_SETTINGS_KEY] = self._metadata

    def __setattr__(self, name, value):
        if name in (
            "context",
            "_metadata",
            "site_settings",
            "annotations",
            "needs_saving",
        ):
            self.__dict__[name] = value
        else:
            self._metadata[name] = value
            self._set()

    def __getattr__(self, name):
        default = None
        if name in ISiteSyndicationSettings.names():
            default = getattr(self.site_settings, name)
        elif name == "enabled" and self.site_settings.default_enabled:
            default = True
        elif name in IFeedSettings.names():
            default = IFeedSettings[name].default

        return self._metadata.get(name, default)
