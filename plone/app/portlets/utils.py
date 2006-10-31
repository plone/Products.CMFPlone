from zope.component import getUtility, getMultiAdapter
from zope.app.container.interfaces import INameChooser

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from plone.app.portlets.portlets import classic
from plone.app.portlets.portlets import login
from plone.app.portlets.portlets import news
from plone.app.portlets.portlets import events

from Acquisition import aq_base

portletsMapping = { 'portlet_login'  : login.Assignment(),
                    'portlet_news'   : news.Assignment(count=5),
                    'portlet_events' : events.Assignment(count=5),
                  }
                  
def convert_legacy_portlets(context):
    """Convert legacy portlets (left_slots, right_slots) in the given
    context to new-style portlets.
    """
        
    # Convert left_slots and right_slots to portlets
    
    left = getUtility(IPortletManager, name='plone.leftcolumn')
    right = getUtility(IPortletManager, name='plone.rightcolumn')
    
    leftAssignable = getMultiAdapter((context, left), IPortletAssignmentMapping)
    rightAssignable = getMultiAdapter((context, right), IPortletAssignmentMapping)
    
    leftChooser = INameChooser(leftAssignable)
    rightChooser = INameChooser(rightAssignable)
    
    left_slots = getattr(aq_base(context), 'left_slots', [])
    right_slots = getattr(aq_base(context), 'right_slots', [])
            
    for item in left_slots:
        path = item.split('/')
        if len(path) == 4:
            newPortlet = portletsMapping.get(path[1], None)
            if newPortlet is None and path[0] in ('context', 'here',) and path[2] == 'macros':
                newPortlet = classic.Assignment(path[1], path[3])
            if newPortlet is not None:
                leftAssignable[leftChooser.chooseName(None, newPortlet)] = newPortlet
                
    for item in right_slots:
        path = item.split('/')
        if len(path) == 4:
            newPortlet = portletsMapping.get(path[1], None)
            if newPortlet is None and path[0] in ('context', 'here',) and path[2] == 'macros':
                newPortlet = classic.Assignment(path[1], path[3])
            if newPortlet is not None:
                rightAssignable[rightChooser.chooseName(None, newPortlet)] = newPortlet
                
    context.left_slots = []
    context.right_slots = []