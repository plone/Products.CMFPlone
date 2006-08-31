from zope.interface import implements
from zope.component import adapts, getUtility, getMultiAdapter

from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces.http import IHTTPRequest

from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from plone.portlets.constants import USER_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import CONTENT_TYPE_CATEGORY

from plone.app.portlets.storage import PortletAssignmentMapping

from Acquisition import aq_base

class ContextPortletNamespace(object):
    """Used to traverse to a contextual portlet assignable
    """
    implements(ITraversable)
    adapts(ILocalPortletAssignable, IHTTPRequest)
    
    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        
    def traverse(self, name, ignore):
        column = getUtility(IPortletManager, name=name)
        manager = getMultiAdapter((self.context, column,), IPortletAssignmentMapping)
        return manager

class CurrentUserPortletNamespace(object):
    """Used to traverse to a portlet assignable for the current user.
    """
    implements(ITraversable)
    adapts(ISiteRoot, IHTTPRequest)
    
    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        
    def traverse(self, name, ignore):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.isAnonymousUser():
            raise KeyError, "Cannot get current user portlets for anonymous"
        user = mtool.getAuthenticatedMember().getId()
        col = name
        column = getUtility(IPortletManager, name=col)
        category = column[USER_CATEGORY]
        manager = category.get(user, None)
        if manager is None:
            manager = category[user] = PortletAssignmentMapping()
        return manager
        
class UserPortletNamespace(object):
    """Used to traverse to a user portlet assignable
    """
    implements(ITraversable)
    adapts(ISiteRoot, IHTTPRequest)
    
    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        
    def traverse(self, name, ignore):
        col, user = name.split('+')
        column = getUtility(IPortletManager, name=col)
        category = column[USER_CATEGORY]
        manager = category.get(user, None)
        if manager is None:
            manager = category[user] = PortletAssignmentMapping()
        return manager

class GroupPortletNamespace(object):
    """Used to traverse to a group portlet assignable
    """
    implements(ITraversable)
    adapts(ISiteRoot, IHTTPRequest)
    
    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        
    def traverse(self, name, ignore):
        col, group = name.split('+')
        column = getUtility(IPortletManager, name=col)
        category = column[GROUP_CATEGORY]
        manager = category.get(group, None)
        if manager is None:
            manager = category[group] = PortletAssignmentMapping()
        return manager

class ContentTypePortletNamespace(object):
    """Used to traverse to a content type portlet assignable
    """
    implements(ITraversable)
    adapts(ISiteRoot, IHTTPRequest)
    
    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        
    def traverse(self, name, ignore):
        col, pt = name.split('+')
        column = getUtility(IPortletManager, name=col)
        category = column[CONTENT_TYPE_CATEGORY]
        manager = category.get(pt, None)
        if manager is None:
            manager = category[pt] = PortletAssignmentMapping()
        return manager