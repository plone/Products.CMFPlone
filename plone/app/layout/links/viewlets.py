from plone.app.layout.viewlets import ViewletBase
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class FaviconViewlet(ViewletBase):
    render = ViewPageTemplateFile('favicon.pt')


class SearchViewlet(ViewletBase):
    render = ViewPageTemplateFile('search.pt')


class AuthorViewlet(ViewletBase):
    render = ViewPageTemplateFile('author.pt')


class NavigationViewlet(ViewletBase):
    render = ViewPageTemplateFile('navigation.pt')
