from plone.memoize import ram
from plone.memoize.compress import xhtml_compress

from zope.component import getMultiAdapter
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets import ViewletBase
from plone.app.layout.viewlets.common import get_language
from plone.app.layout.viewlets.common import render_cachekey

from Products.CMFCore.utils import getToolByName


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

    render = ViewPageTemplateFile('author.pt')


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

    render = ViewPageTemplateFile('rsslink.pt')
