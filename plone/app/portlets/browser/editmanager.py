from Acquisition import Explicit, aq_parent, aq_inner

from zope.interface import implements, Interface
from zope.component import adapts, getMultiAdapter, getUtilitiesFor

from zope.annotation.interfaces import IAnnotations

from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.interfaces.browser import IBrowserRequest

from zope.contentprovider.interfaces import UpdateNotCalled

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletRetriever
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPlacelessPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import ILocalPortletAssignmentManager

from plone.portlets.constants import CONTEXT_ASSIGNMENT_KEY

from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import CONTENT_TYPE_CATEGORY

from plone.app.portlets.browser.interfaces import IManagePortletsView

from Products.Five.browser import BrowserView 
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

class EditPortletManagerRenderer(Explicit):
    """Render a portlet manager in edit mode.
    """
    implements(IPortletManagerRenderer)
    adapts(Interface, IBrowserRequest, IManagePortletsView, IPortletManager)

    def __init__(self, context, request, view, manager):
        self.__parent__ = view
        self.manager = manager # part of interface
        self.context = context
        self.request = request
        self.template = ZopeTwoPageTemplateFile('editmanager.pt')
        self.__updated = False
        self.__assignments = None
        self.__portlets = None
        
    @property
    def visible(self):
        True

    def filter(self, portlets):
        return portlets

    def update(self):
        self.__updated = True
        for p in self._lazyLoadPortlets():
            p.update()

    def render(self):
        if not self.__updated:
            raise UpdateNotCalled()
        return self.template()
    
    # Used by the view template

    def portlets(self):
        baseUrl = self.__parent__.getAssignmentMappingUrl(self.manager)
        assignments = self._lazyLoadAssignments()
        portlets = self._lazyLoadPortlets()
        assert len(assignments) == len(portlets)
        data = []
        for idx in range(len(assignments)):
            name = assignments[idx].__name__
            data.append( {'title'      : assignments[idx].title,
                          'html'       : portlets[idx].render(),
                          'editview'   : '%s/%s/edit.html' % (baseUrl, name),
                          'up_url'     : '%s/@@move-portlet-up?name=%s' % (baseUrl, name),
                          'down_url'   : '%s/@@move-portlet-down?name=%s' % (baseUrl, name),
                          'delete_url' : '%s/@@delete-portlet?name=%s' % (baseUrl, name),
                          })
        if len(data) > 0:
            data[0]['up_url'] = data[-1]['down_url'] = None
        return data
        
    def context_blacklist_status(self):
        assignable = getMultiAdapter((self.context, self.manager,), ILocalPortletAssignmentManager)
        return assignable.getBlacklistStatus(CONTEXT_CATEGORY)

    def user_blacklist_status(self):
        assignable = getMultiAdapter((self.context, self.manager,), ILocalPortletAssignmentManager)
        return assignable.getBlacklistStatus(USER_CATEGORY)
    
    def group_blacklist_status(self):
        assignable = getMultiAdapter((self.context, self.manager,), ILocalPortletAssignmentManager)
        return assignable.getBlacklistStatus(GROUP_CATEGORY)
    
    def content_type_blacklist_status(self):
        assignable = getMultiAdapter((self.context, self.manager,), ILocalPortletAssignmentManager)
        return assignable.getBlacklistStatus(CONTENT_TYPE_CATEGORY)
        
    def addable_portlets(self):
        baseUrl = self.__parent__.getAssignmentMappingUrl(self.manager)
        return [ {'title' : p[1].title,
                  'description' : p[1].description,
                  'addview' : '%s/+/%s' % (baseUrl, p[1].addview,),
                  } for p in getUtilitiesFor(IPortletType)]
        
    def _lazyLoadPortlets(self):
        if self.__portlets is None:
            assignments = self._lazyLoadAssignments()
            self.__portlets = [self._dataToPortlet(a.data)
                                for a in self.filter(assignments)]
        return self.__portlets
    
    def _lazyLoadAssignments(self):
        if self.__assignments is None:
            self.__assignments = self.__parent__.getAssignmentsForManager(self.manager)
        return self.__assignments
    
    def _dataToPortlet(self, data):
        """Helper method to get the correct IPortletRenderer for the given
        data object.
        """
        portlet = getMultiAdapter((self.context, self.request, self.__parent__,
                                    self.manager, data,), IPortletRenderer)
        return portlet.__of__(self.context)
        
class ManagePortletAssignments(BrowserView):
    """Utility views for managing portlets for a particular column
    """
    
    # view @@move-portlet-up
    def move_portlet_up(self, name):
        assignments = aq_inner(self.context)
        keys = list(assignments.keys())
        
        idx = keys.index(name)
        keys.remove(name)
        keys.insert(idx-1, name)
        assignments.updateOrder(keys)
        
        self.request.response.redirect(self._nextUrl())
        return ''
    
    # view @@move-portlet-down
    def move_portlet_down(self, name):
        assignments = aq_inner(self.context)
        keys = list(assignments.keys())
        
        idx = keys.index(name)
        keys.remove(name)
        keys.insert(idx+1, name)
        assignments.updateOrder(keys)
        
        self.request.response.redirect(self._nextUrl())
        return ''
    
    # view @@delete-portlet
    def delete_portlet(self, name):
        assignments = aq_inner(self.context)
        del assignments[name]
        self.request.response.redirect(self._nextUrl())
        return ''
        
    def _nextUrl(self):
        referer = self.request.get('HTTP_REFERER', None)
        if referer is None:
            context = aq_parent(aq_inner(self.context))
            url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))    
            referer = '%s/@@manage-portlets' % (url,)
        return referer