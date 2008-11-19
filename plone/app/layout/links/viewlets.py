from zope.component import getMultiAdapter
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets import ViewletBase

from Products.CMFCore.utils import getToolByName


class FaviconViewlet(ViewletBase):

    render = ViewPageTemplateFile('favicon.pt')


class SearchViewlet(ViewletBase):

    render = ViewPageTemplateFile('search.pt')


class AuthorViewlet(ViewletBase):

    render = ViewPageTemplateFile('author.pt')


class NavigationViewlet(ViewletBase):

    render = ViewPageTemplateFile('navigation.pt')


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
