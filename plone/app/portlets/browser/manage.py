from zope.interface import implements
from zope.component import getMultiAdapter, getUtility

from Products.Five import BrowserView
from Acquisition import aq_base

from Products.CMFCore.utils import getToolByName

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import ILocalPortletAssignmentManager

from plone.portlets.constants import USER_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import CONTENT_TYPE_CATEGORY
from plone.portlets.constants import CONTEXT_CATEGORY

from plone.app.portlets.storage import PortletAssignmentMapping

from plone.app.portlets.browser.interfaces import IManagePortletsView
from plone.app.portlets.browser.interfaces import IManageContextualPortletsView
from plone.app.portlets.browser.interfaces import IManageDashboardPortletsView
from plone.app.portlets.browser.interfaces import IManageGroupPortletsView
from plone.app.portlets.browser.interfaces import IManageContentTypePortletsView

from plone.app.portlets import utils

class ManageContextualPortlets(BrowserView):
    implements(IManageContextualPortletsView)
        
    # IManagePortletsView implementation
    
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
    def set_blacklist_status(self, manager, user_status, group_status, content_type_status, context_status):
        portletManager = getUtility(IPortletManager, name=manager)
        assignable = getMultiAdapter((self.context, portletManager,), ILocalPortletAssignmentManager)
        
        def int2status(status):
            if status == 0:
                return None
            elif status > 0:
                return True
            else:
                return False
        
        assignable.setBlacklistStatus(USER_CATEGORY, int2status(user_status))
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
    
    def getAssignmentMappingUrl(self, manager):
        baseUrl = str(getMultiAdapter((self.context, self.request), name='absolute_url'))
        return '%s/++dashboard++' % (baseUrl, )

    def getAssignmentsForManager(self, manager):
        userId = self._getUserId()
        column = getUtility(IPortletManager, name=manager.__name__)
        category = column[USER_CATEGORY]
        mapping = category.get(userId, None)
        if mapping is None:
            mapping = category[userId] = PortletAssignmentMapping()
        return mapping.values()
    
    def _getUserId(self):
        membership = getToolByName(self.context, 'portal_membership', None)
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
    
    def getAssignmentMappingUrl(self, manager):
        baseUrl = str(getMultiAdapter((self.context, self.request), name='absolute_url'))
        groupId = self.request.get('groupId', None)
        if groupId is None:
            groupId = self.groups()[0]
        return '%s/++groupportlets++%s+%s' % (baseUrl, manager.__name__, groupId)

    def getAssignmentsForManager(self, manager):
        groupId = self.request.get('groupId', None)
        if groupId is None:
            groupId = self.groups()[0]
        column = getUtility(IPortletManager, name=manager.__name__)
        category = column[GROUP_CATEGORY]
        mapping = category.get(groupId, None)
        if mapping is None:
            mapping = category[groupId] = PortletAssignmentMapping()
        return mapping.values()
    
    # View attributes
    
    def groups(self):
        portal_groups = getToolByName(self.context, 'portal_groups')
        return sorted(portal_groups.getGroupIds())

class ManageContentTypePortlets(BrowserView):
    implements(IManageContentTypePortletsView)
        
    # IManagePortletsView implementation
    
    def getAssignmentMappingUrl(self, manager):
        baseUrl = str(getMultiAdapter((self.context, self.request), name='absolute_url'))
        pt = self.request.get('portal_type', None)
        if pt is None:
            pt = self.portal_types()[0]['id']
        return '%s/++contenttypeportlets++%s+%s' % (baseUrl, manager.__name__, pt)

    def getAssignmentsForManager(self, manager):
        pt = self.request.get('portal_type', None)
        if pt is None:
            pt = self.portal_types()[0]['id']
        column = getUtility(IPortletManager, name=manager.__name__)
        category = column[CONTENT_TYPE_CATEGORY]
        mapping = category.get(pt, None)
        if mapping is None:
            mapping = category[pt] = PortletAssignmentMapping()
        return mapping.values()
    
    # View attributes
    
    def portal_types(self):
        portal_types = getToolByName(self.context, 'portal_types')
        pts = []
        for fti in portal_types.listTypeInfo():
            pts.append({ 'id'           : fti.getId(),
                         'title'        : fti.Title(),
                         'description'  : fti.Description()})
        pts.sort(lambda x, y: cmp(x['title'], y['title']))
        return pts

