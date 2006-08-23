from types import StringTypes

from zope.interface import implements, Interface
from zope.component import adapts

from Acquisition import aq_parent, aq_base, aq_inner
from OFS.interfaces import ITraversable

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.interfaces import IReferenceable

from plone.portlets.interfaces import IPortletContext

class ContentContext(object):
    """A portlet context for regular content items.
    
    Note - we register this for ITraversable so that it can also work for
    tools and other non-content items. This may hijack the context in non-CMF
    contexts, but that is doubtfully going to be an issue.
    """
    implements(IPortletContext)
    adapts(ITraversable)
    
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
        return aq_parent(aq_inner(self.context))
    
    @property
    def userId(self):
        membership = getToolByName(self.context, 'portal_membership', None)
        if membership is None or membership.isAnonymousUser():
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
        membership = getToolByName(self.context, 'portal_membership', None)
        if membership is None or membership.isAnonymousUser():
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