from zExceptions import NotFound
from Products.Five import BrowserView

from zope.schema.interfaces import IVocabularyFactory
from zope.interface import implementer
from zope.component import getUtility

from Products.CMFPlone.interfaces.syndication import ISyndicationUtil
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from Products.CMFPlone.interfaces.syndication import ISiteSyndicationSettings
from Products.CMFPlone.interfaces.syndication import ISyndicatable

from plone.registry.interfaces import IRegistry
from plone.memoize.view import memoize


@implementer(ISyndicationUtil)
class SyndicationUtil(BrowserView):

    def allowed_feed_types(self):
        settings = IFeedSettings(self.context)
        factory = getUtility(IVocabularyFactory,
                             "plone.app.vocabularies.SyndicationFeedTypes")
        vocabulary = factory(self.context)
        types = []
        for typ in settings.feed_types:
            types.append(vocabulary.getTerm(typ))
        return [{'path': t.value, 'title': t.title} for t in types]

    def rss_url(self):
        settings = IFeedSettings(self.context)
        types = settings.feed_types
        url = self.context.absolute_url()
        if len(types) == 0:
            return url
        _type = types[0]
        return f'{url}/{_type}'

    def context_allowed(self):
        if not ISyndicatable.providedBy(self.context):
            return False
        elif not self.site_enabled():
            return False
        return True

    def context_enabled(self, raise404=False):
        settings = IFeedSettings(self.context, None)
        if not self.context_allowed() or not settings.enabled:
            if raise404:
                raise NotFound
            else:
                return False
        else:
            return True

    @property
    @memoize
    def site_settings(self):
        try:
            registry = getUtility(IRegistry)
            return registry.forInterface(ISiteSyndicationSettings)
        except KeyError:
            return None

    def site_enabled(self):
        try:
            settings = self.site_settings
            return settings.allowed
        except AttributeError:
            return True

    def search_rss_enabled(self, raise404=False):
        try:
            settings = self.site_settings
            if settings.search_rss_enabled:
                return True
            elif raise404:
                raise NotFound
            else:
                return False
        except AttributeError:
            return True

    def show_author_info(self):
        try:
            settings = self.site_settings
            return settings.show_author_info
        except AttributeError:
            return True

    def max_items(self):
        try:
            settings = self.site_settings
            return settings.max_items
        except AttributeError:
            return 15
