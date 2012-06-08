from zExceptions import NotFound
from zope.interface import implements
from zope.component import queryAdapter
from Products.Five import BrowserView
from Products.CMFPlone.interfaces.syndication import IFeed
from Products.CMFPlone.interfaces.syndication import ISearchFeed
from Products.CMFPlone.interfaces.syndication import ISyndicationUtil
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from Products.CMFPlone.interfaces.syndication import ISiteSyndicationSettings
from Products.CMFPlone.interfaces.syndication import ISyndicatable
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.memoize.view import memoize


_feed_type_infos = {
    'atom.xml': {
        'path': 'atom.xml',
        'content-type': 'application/atom+xml',
        'title': 'Atom'
    },
    'rss.xml': {
        'path': 'rss.xml',
        'content-type': 'application/rss+xml',
        'title': 'RSS 1.0'
    },
    'itunes.xml': {
        'path': 'itunes.xml',
        'content-type': 'application/rss+xml',
        'title': 'iTunes'
    }
}


class SyndicationTool(BrowserView):
    implements(ISyndicationUtil)

    def adapter(self, full_objects=False):
        if not ISyndicatable.providedBy(self.context):
            return
        adpt = queryAdapter(self.context, IFeed)
        if adpt is not None and full_objects:
            adpt.full_objects = True
        return adpt

    def search_adapter(self):
        adpt = queryAdapter(self.context, ISearchFeed)
        adpt.full_objects = True
        return adpt

    def allowed_feed_types(self):
        settings = IFeedSettings(self.context)
        return [_feed_type_infos[t] for t in settings.feed_types]

    def context_allowed(self):
        if not ISyndicatable.providedBy(self.context):
            return False
        elif not self.site_enabled():
            return False
        return True

    def context_enabled(self):
        if not self.context_allowed():
            return False
        settings = IFeedSettings(self.context)
        return settings.enabled

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
            return settings.enabled
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
            settings = settings = self.site_settings
            return settings.max_items
        except AttributeError:
            return 15
