from StringIO import StringIO

from plone.memoize import ram
from plone.memoize import view
from plone.memoize.compress import xhtml_compress
from zope.component import getMultiAdapter

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets import ViewletBase
from plone.app.uuid.utils import uuidToObject
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import ISecuritySchema
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from Products.CMFPlone.interfaces.syndication import ISiteSyndicationSettings


def get_language(context, request):
    portal_state = getMultiAdapter((context, request),
                                   name=u'plone_portal_state')
    return portal_state.language()


def render_cachekey(fun, self):
    key = StringIO()
    # Include the name of the viewlet as the underlying cache key only
    # takes the module and function name into account, but not the class
    print >> key, self.__name__
    print >> key, self.site_url
    print >> key, get_language(aq_inner(self.context), self.request)

    return key.getvalue()


class FaviconViewlet(ViewletBase):

    _template = ViewPageTemplateFile('favicon.pt')

    @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())


class SearchViewlet(ViewletBase):

    _template = ViewPageTemplateFile('search.pt')

    @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())


class AuthorViewlet(ViewletBase):

    _template = ViewPageTemplateFile('author.pt')

    def update(self):
        super(AuthorViewlet, self).update()
        self.tools = getMultiAdapter((self.context, self.request),
                                     name='plone_tools')

    def show(self):
        anonymous = self.portal_state.anonymous()
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISecuritySchema,
            prefix='plone',
        )
        return not anonymous or settings.allow_anon_views_about

    def render(self):
        if self.show():
            return self._template()
        return u''


class RSSViewlet(ViewletBase):

    def getRssLinks(self, obj):
        settings = IFeedSettings(obj, None)
        if settings is None:
            return []
        factory = getUtility(
            IVocabularyFactory, "plone.app.vocabularies.SyndicationFeedTypes")
        vocabulary = factory(self.context)
        urls = []
        for typ in settings.feed_types:
            try:
                term = vocabulary.getTerm(typ)
            except LookupError:
                continue
            urls.append({
                'title': '%s - %s' % (
                    obj.Title(), term.title),
                'url': obj.absolute_url() + '/' + term.value})
        return urls

    def update(self):
        super(RSSViewlet, self).update()
        self.rsslinks = []
        portal = self.portal_state.portal()
        util = getMultiAdapter((self.context, self.request),
                               name="syndication-util")
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        if context_state.is_portal_root():
            if util.site_enabled():
                registry = getUtility(IRegistry)
                try:
                    settings = registry.forInterface(ISiteSyndicationSettings)
                except KeyError:
                    return
                if settings.site_rss_items:
                    for uid in settings.site_rss_items:
                        if not uid:
                            continue
                        obj = uuidToObject(uid)
                        if obj is None and uid[0] == '/':
                            obj = portal.restrictedTraverse(uid.lstrip('/'), None)
                        if obj is not None:
                            self.rsslinks.extend(self.getRssLinks(obj))
                self.rsslinks.extend(self.getRssLinks(portal))
        else:
            if util.context_enabled():
                self.rsslinks.extend(self.getRssLinks(self.context))

    index = ViewPageTemplateFile('rsslink.pt')


class CanonicalURL(ViewletBase):
    """Defines a canonical link relation viewlet to be displayed across the
    site. A canonical page is the preferred version of a set of pages with
    highly similar content. For more information, see:
    https://tools.ietf.org/html/rfc6596
    https://support.google.com/webmasters/answer/139394?hl=en
    """

    @view.memoize
    def render(self):
        context_state = getMultiAdapter(
            (self.context, self.request), name=u'plone_context_state')
        canonical_url = context_state.canonical_object_url()
        return u'    <link rel="canonical" href="%s" />' % canonical_url
