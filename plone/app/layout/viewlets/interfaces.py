from zope.viewlet.interfaces import IViewletManager
    
class IHtmlHead(IViewletManager):
    """A viewlet manager that sits in the <head> of the rendered page
    """

class IPortalHeader(IViewletManager):
    """A viewlet manager that sits at the very top of the rendered page
    """

class IAboveContent(IViewletManager):
    """A viewlet manager that sits above the content area
    """

class IBelowContent(IViewletManager):
    """A viewlet manager that sits below the content area
    """
    
class IPortalFooter(IViewletManager):
    """A viewlet manager that sits in the portal footer
    """