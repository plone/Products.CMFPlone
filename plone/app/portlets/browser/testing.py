from zope.interface import implements
from zope.component import getMultiAdapter
from Products.Five import BrowserView

from Acquisition import aq_base

from Products.CMFCore.utils import getToolByName

from plone.portlets.interfaces import IPortletContext
from plone.portlets.interfaces import IPortletAssignable

from plone.app.portlets.portlets.classic import ClassicPortletAssignment

class Testing(BrowserView):
    
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self):
        
        import pdb; pdb.set_trace()
        
        # Convert left_slots and right_slots to portlets
        
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        left = portal['.portlets']['left']
        right = portal['.portlets']['right']
        
        left_slots = getattr(aq_base(self.context), 'left_slots', [])
        right_slots = getattr(aq_base(self.context), 'right_slots', [])
        
        portletContext = IPortletContext(self.context)
        
        leftAssignments = []
        rightAssignments = []
        
        for item in left_slots:
            path = item.split('/')
            if len(path) == 4 and path[0] in ('context', 'here',) and path[2] == 'macros':
                leftAssignments.append(ClassicPortletAssignment(path[1], path[3]))
        for item in right_slots:
            path = item.split('/')
            if len(path) == 4 and path[0] in ('context', 'here',) and path[2] == 'macros':
                rightAssignments.append(ClassicPortletAssignment(path[1], path  [3]))
        
        leftAssignable = getMultiAdapter((portletContext, left), IPortletAssignable)
        rightAssignable = getMultiAdapter((portletContext, right), IPortletAssignable)
        
        leftAssignable.setPortletAssignments(leftAssignments)
        rightAssignable.setPortletAssignments(rightAssignments)