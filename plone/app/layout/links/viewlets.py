from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile


class FaviconViewlet(ViewletBase):
    render = ZopeTwoPageTemplateFile('favicon.pt')


class SearchViewlet(ViewletBase):
    render = ZopeTwoPageTemplateFile('search.pt')


class AuthorViewlet(ViewletBase):
    render = ZopeTwoPageTemplateFile('author.pt')


class NavigationViewlet(ViewletBase):
    render = ZopeTwoPageTemplateFile('navigation.pt')
