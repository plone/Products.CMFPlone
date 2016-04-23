# -*- coding: utf-8 -*-
from zope.viewlet.interfaces import IViewletManager


class IHTTPHeaders(IViewletManager):
    """ A viewlet manager that sits before <head> to set headers to the
        request.
    """


class IHtmlHead(IViewletManager):
    """A viewlet manager that sits in the <head> of the rendered page
    """


class IHtmlHeadLinks(IViewletManager):
    """ A viewlet manager that sits in the <head> and is responsible
        for semantic navigation links, the favicon, rss links and more
        provided by <link> tags.
    """


class IPortalTop(IViewletManager):
    """A viewlet manager that sits at the very top of the rendered page
    """


class IMainNavigation(IViewletManager):
    """A viewlet manager that holds the main navigation viewlet
    """


class IGlobalStatusMessage(IViewletManager):
    """ A viewlet manager that is aside the content to render messages for
        the user.
    """


class IPortalHeader(IViewletManager):
    """A viewlet manager that sits right after the skip to content links
    """


class IToolbar(IViewletManager):
    """A viewlet manager that sits above all content, normally used to hold
    the toolbar containing content views (tabs), associated actions and the
    personal tools.
    """


class IAboveContent(IViewletManager):
    """A viewlet manager that sits above the content area
    """


class IAboveContentTitle(IViewletManager):
    """A viewlet manager that sits above the content title in view templates
    """


class IDocumentActions(IViewletManager):
    """A viewlet manager that sits near the content heading
    """


class IBelowContentTitle(IViewletManager):
    """A viewlet manager that sits below the content title in view templates
    """


class IAboveContentBody(IViewletManager):
    """A viewlet manager that sits above the content body in view templates
    """


class IBelowContentBody(IViewletManager):
    """A viewlet manager that sits below the content body in view templates
    """


class IBelowContent(IViewletManager):
    """A viewlet manager that sits below the content area
    """


class IPortalFooter(IViewletManager):
    """A viewlet manager that sits in the portal footer
    """


class IScripts(IViewletManager):
    """A viewlet manager that stores the script tags
    """
