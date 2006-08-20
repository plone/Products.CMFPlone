from types import StringTypes

from zope.interface import implements
from zope.component import adapts

from Acquisition import aq_parent, aq_base

from Products.CMFCore.interfaces import IDynamicType
from Products.CMFCore.interfaces import ISiteRoot

from Products.CMFCore.utils import getToolByName

from Products.Archetypes.interfaces import IReferenceable

from plone.portlets.interfaces import IPortletContext

class ContentContext(object):
    """A portlet context for regular content items.
    """
    implements(IPortletContext)
    adapts(IDynamicType)
    
    def __init__(self, context):
        self.context = context
    
    @property
    def uid(self):
        referenceable = IReferenceable(self.context, None)
        if referenceable is not None:
            return referenceable.UID()
        else:
            return '/'.join(self.context.getPhysicalPath())
        
    @property
    def parent(self):
        return aq_parent(self.context)
    
    @property
    def userId(self):
        membership = getToolByName(self.context, 'portal_membership')
        if membership.isAnonymousUser():
            return None
        
        member = membership.getAuthenticatedMember()
        if not member:
            return None
        
        try:
            memberId = member.getUserId()
        except AttributeError:
            memberId = member.getId()

        if not memberId:
            return None
        
        return memberId
        
    @property                     
    def groupIds(self):
        membership = getToolByName(self.context, 'portal_membership')
        if membership.isAnonymousUser():
            return ()
        
        member = membership.getAuthenticatedMember()
        if not member:
            return ()
            
        groups = member.getGroups()
        
        # Ensure we get the list of ids - getGroups() suffers some acquision
        # ambiguity - the Plone member-data version returns ids.
        
        for group in groups:
            if type(group) not in StringTypes:
                return ()
                
        return tuple(groups)
    
class PortalRootContext(ContentContext):
    """A portlet context for the site root.
    """

    implements(IPortletContext)
    adapts(ISiteRoot)
    
    def __init__(self, context):
        self.context = context
        
    @property
    def parent(self):
        return None