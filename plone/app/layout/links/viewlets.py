from zope.interface import implements
from zope.viewlet.interfaces import IViewlet

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Products.CMFCore.utils import getToolByName


class ViewletBase(BrowserView):
    """ Base class with common functions for link viewlets.
    """
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(ViewletBase, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def update(self):
        pass

    def render(self):
        raise NotImplementedError(
            '`render` method must be implemented by subclass.')

    def portal_url(self):
        tool = getToolByName(self.context, 'portal_url')
        portal = tool.getPortalObject()
        return portal.absolute_url()


class FaviconViewlet(ViewletBase):
    render = ZopeTwoPageTemplateFile('favicon.pt')


class SearchViewlet(ViewletBase):
    render = ZopeTwoPageTemplateFile('search.pt')


class AuthorViewlet(ViewletBase):
    render = ZopeTwoPageTemplateFile('author.pt')


class NavigationViewlet(ViewletBase):
    render = ZopeTwoPageTemplateFile('navigation.pt')
