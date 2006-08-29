from zope.interface import implements
from zope.component import getMultiAdapter, getUtility
from Products.Five import BrowserView

from Acquisition import aq_base

from Products.CMFCore.utils import getToolByName

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignmentManager

from plone.app.portlets.portlets.classic import ClassicPortletAssignment
from plone.app.portlets.portlets.login import LoginPortletAssignment

from plone.app.portlets.browser.interfaces import IManagePortletsView

class ManagePortlets(BrowserView):
    implements(IManagePortletsView)
    
    def has_legacy_portlets(self):
        left_slots = getattr(aq_base(self.context), 'left_slots', [])
        right_slots = getattr(aq_base(self.context), 'right_slots', [])
        
        return left_slots or right_slots
    
    # view @@convert-legacy-portlets
    
    def convert_legacy_portlets(self):
        
        portletsMapping = { 'portlet_login' : LoginPortletAssignment() }
        
        # Convert left_slots and right_slots to portlets
        
        left = getUtility(IPortletManager, name='plone.leftcolumn')
        right = getUtility(IPortletManager, name='plone.rightcolumn')
        
        leftAssignable = getMultiAdapter((self.context, left), ILocalPortletAssignmentManager)
        rightAssignable = getMultiAdapter((self.context, right), ILocalPortletAssignmentManager)
        
        left_slots = getattr(aq_base(self.context), 'left_slots', [])
        right_slots = getattr(aq_base(self.context), 'right_slots', [])
                
        for item in left_slots:
            path = item.split('/')
            if len(path) == 4:
                newPortlet = portletsMapping.get(path[1], None)
                if newPortlet is not None:
                     leftAssignable.saveAssignment(newPortlet)
                elif path[0] in ('context', 'here',) and path[2] == 'macros':
                    leftAssignable.saveAssignment(ClassicPortletAssignment(path[1], path[3]))
        for item in right_slots:
            path = item.split('/')
            if len(path) == 4:
                newPortlet = portletsMapping.get(path[1], None)
                if newPortlet is not None:
                     rightAssignable.saveAssignment(newPortlet)
                elif path[0] in ('context', 'here',) and path[2] == 'macros':
                    rightAssignable.saveAssignment(ClassicPortletAssignment(path[1], path[3]))
                    
        self.context.left_slots = []
        self.context.right_slots = []
                    
        self.context.request.response.redirect(self.context.absolute_url() + '/@@manage-portlets')