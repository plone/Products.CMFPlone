from StringIO import StringIO

from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from zope.component import getMultiAdapter

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets import ViewletBase


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
        properties = self.tools.properties()
        site_properties = getattr(properties, 'site_properties')
        anonymous = self.portal_state.anonymous()
        allowAnonymousViewAbout = site_properties.getProperty('allowAnonymousViewAbout', True)
        return not anonymous or allowAnonymousViewAbout

    def render(self):
        if self.show():
            return self._template()
        return u''


class NavigationViewlet(ViewletBase):

    _template = ViewPageTemplateFile('navigation.pt')

    @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())


class RSSViewlet(ViewletBase):

    def update(self):
        super(RSSViewlet, self).update()
        syntool = getToolByName(self.context, 'portal_syndication')
        if syntool.isSyndicationAllowed(self.context):
            self.allowed = True
            context_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_context_state')
            self.url = '%s/RSS' % context_state.object_url()
        else:
            self.allowed = False

    index = ViewPageTemplateFile('rsslink.pt')
