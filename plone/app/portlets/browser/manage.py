from zope.interface import implements
from zope.component import getMultiAdapter, getUtility

from AccessControl import Unauthorized
from Acquisition import aq_base
from Products.Five import BrowserView

from Products.CMFCore.interfaces import IMembershipTool
from Products.CMFCore.interfaces import ITypesTool

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import ILocalPortletAssignmentManager

from plone.portlets.constants import USER_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import CONTENT_TYPE_CATEGORY
from plone.portlets.constants import CONTEXT_CATEGORY

from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.storage import UserPortletAssignmentMapping

from plone.app.portlets.interfaces import IPortletPermissionChecker

from plone.app.portlets.browser.interfaces import IManageContextualPortletsView
from plone.app.portlets.browser.interfaces import IManageDashboardPortletsView
from plone.app.portlets.browser.interfaces import IManageGroupPortletsView
from plone.app.portlets.browser.interfaces import IManageContentTypePortletsView

from plone.app.portlets import utils

class ManageContextualPortlets(BrowserView):
    implements(IManageContextualPortletsView)
    
    def __init__(self, context, request):
        super(ManageContextualPortlets, self).__init__(context, request)
        self.request.set('disable_border', True)
        
    # IManagePortletsView implementation
    
    @property
    def category(self):
        return CONTEXT_CATEGORY
        
    @property
    def key(self):
        return '/'.join(self.context.getPhysicalPath())
    
    def getAssignmentMappingUrl(self, manager):
        baseUrl = str(getMultiAdapter((self.context, self.request), name='absolute_url'))
        return '%s/++contextportlets++%s' % (baseUrl, manager.__name__)
    
    def getAssignmentsForManager(self, manager):
        assignments = getMultiAdapter((self.context, manager), IPortletAssignmentMapping)
        return assignments.values()
    
    # view @@manage-portlets
    
    def has_legacy_portlets(self):
        left_slots = getattr(aq_base(self.context), 'left_slots', [])
        right_slots = getattr(aq_base(self.context), 'right_slots', [])
        
        return (left_slots or right_slots)

    # view @@set-portlet-blacklist-status
    def set_blacklist_status(self, manager, group_status, content_type_status, context_status):
        portletManager = getUtility(IPortletManager, name=manager)
        assignable = getMultiAdapter((self.context, portletManager,), ILocalPortletAssignmentManager)
        
        IPortletPermissionChecker(assignable)()
        
        def int2status(status):
            if status == 0:
                return None
            elif status > 0:
                return True
            else:
                return False
        
        assignable.setBlacklistStatus(GROUP_CATEGORY, int2status(group_status))
        assignable.setBlacklistStatus(CONTENT_TYPE_CATEGORY, int2status(content_type_status))
        assignable.setBlacklistStatus(CONTEXT_CATEGORY, int2status(context_status))
        
        baseUrl = str(getMultiAdapter((self.context, self.request), name='absolute_url'))
        self.request.response.redirect(baseUrl + '/@@manage-portlets')
        return ''
    
    # view @@convert-legacy-portlets
    
    def convert_legacy_portlets(self):
        utils.convert_legacy_portlets(self.context)
        self.context.request.response.redirect(self.context.absolute_url() + '/@@manage-portlets')

class ManageDashboardPortlets(BrowserView):
    implements(IManageDashboardPortletsView)
        
    # IManagePortletsView implementation
    
    @property
    def category(self):
        return USER_CATEGORY
        
    @property
    def key(self):
        return self._getUserId()
    
    def getAssignmentMappingUrl(self, manager):
        baseUrl = str(getMultiAdapter((self.context, self.request), name='absolute_url'))
        userId = self._getUserId()
        return '%s/++dashboard++%s+%s' % (baseUrl, manager.__name__, userId)

    def getAssignmentsForManager(self, manager):
        userId = self._getUserId()
        column = getUtility(IPortletManager, name=manager.__name__)
        category = column[USER_CATEGORY]
        mapping = category.get(userId, None)
        if mapping is None:
            mapping = category[userId] = UserPortletAssignmentMapping()
        return mapping.values()
    
    def _getUserId(self):
        membership = getUtility(IMembershipTool)
        if membership.isAnonymousUser():
            raise Unauthorized, "Cannot get portlet assignments for anonymous through this view"
        
        member = membership.getAuthenticatedMember()
        try:
            memberId = member.getUserId()
        except AttributeError:
            memberId = member.getId()
        
        if memberId is None:
            raise KeyError, "Cannot find user id of current user" 
        
        return memberId

class ManageGroupPortlets(BrowserView):
    implements(IManageGroupPortletsView)
        
    # IManagePortletsView implementation
    
    @property
    def category(self):
        return GROUP_CATEGORY
        
    @property
    def key(self):
        return self.request['key']
    
    def __init__(self, context, request):
        super(ManageGroupPortlets, self).__init__(context, request)
        self.request.set('disable_border', True)
    
    def getAssignmentMappingUrl(self, manager):
        baseUrl = str(getMultiAdapter((self.context, self.request), name='absolute_url'))
        key = self.request['key']
        return '%s/++groupportlets++%s+%s' % (baseUrl, manager.__name__, key)

    def getAssignmentsForManager(self, manager):
        key = self.request['key']
        column = getUtility(IPortletManager, name=manager.__name__)
        category = column[GROUP_CATEGORY]
        mapping = category.get(key, None)
        if mapping is None:
            mapping = category[key] = PortletAssignmentMapping()
        return mapping.values()
    
    # View attributes
    
    def group(self):
        return self.request['key']

class ManageContentTypePortlets(BrowserView):
    implements(IManageContentTypePortletsView)
    
    def __init__(self, context, request):
        super(ManageContentTypePortlets, self).__init__(context, request)
        self.request.set('disable_border', True)
        
    # IManagePortletsView implementation
    
    @property
    def category(self):
        return CONTENT_TYPE_CATEGORY
        
    @property
    def key(self):
        return self.request['key']
    
    def getAssignmentMappingUrl(self, manager):
        baseUrl = str(getMultiAdapter((self.context, self.request), name='absolute_url'))
        pt = self.request['key']
        return '%s/++contenttypeportlets++%s+%s' % (baseUrl, manager.__name__, pt)

    def getAssignmentsForManager(self, manager):
        pt = self.request['key']
        column = getUtility(IPortletManager, name=manager.__name__)
        category = column[CONTENT_TYPE_CATEGORY]
        mapping = category.get(pt, None)
        if mapping is None:
            mapping = category[pt] = PortletAssignmentMapping()
        return mapping.values()
    
    # View attributes
    
    def portal_type(self):
        portal_types = getUtility(ITypesTool)
        portal_type = self.request['key']
        for fti in portal_types.listTypeInfo():
            if fti.getId() == portal_type:
                return fti.Title()
        

