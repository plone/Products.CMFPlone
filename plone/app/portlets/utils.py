from zope.component import getSiteManager
from plone.portlets.interfaces import IPortletType
from plone.portlets.registration import PortletType

def registerPortletType(site, name, addview, title, description):
    """Register a new type of portlet.
    
    site should be the Plone site root. The title and description should be
    meaningful metadata about the portlet for the UI.
    
    The addview should be the name of a view registered for 
    plone.app.portlets.browser.interfaces.IPortletAdding.
    """
    sm = getSiteManager(site)
    
    portlet = PortletType()
    portlet.title = title
    portlet.description = description
    portlet.addview = addview
    
    sm.registerUtility(component=portlet, provided=IPortletType, name=addview)
    
def unregisterPortletType(site, addview):
    """Unregister a portlet type.
    
    site should be the Plone site root. The addview should be the name of a view 
    registered for plone.app.portlets.browser.interfaces.IPortletAdding.
    """
    
    sm = getSiteManager(site)
    sm.unregisterUtility(provided=IPortletType, name=addview)
