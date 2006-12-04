from zope.interface import implements
from zope.component import getMultiAdapter
from plone.memoize.view import memoize

from Acquisition import aq_base, aq_inner, aq_parent
from Products.Five.browser import BrowserView

from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.CMFPlone.interfaces.NonStructuralFolder import INonStructuralFolder \
     as z2INonStructuralFolder

from interfaces import IContextState

class ContextState(BrowserView):
    """Information about the state of the current context
    """
    
    implements(IContextState)
    
    @property
    @memoize
    def current_page_url(self):
        url = self.request.get('ACTUAL_URL', self.request.get('URL', None))
        query = self.request.get('QUERY_STRING', None)
        if query:
            url += '?' + query
        return url
        
    @property
    @memoize
    def object_url(self):
        return aq_inner(self.context).absolute_url()
        
    @property
    @memoize
    def object_title(self):
        tools = getMultiAdapter((self.context, self.request), name='plone_tools')
        return tools.plone_utils.pretty_title_or_id(aq_inner(self.context))
        
    @property
    @memoize
    def workflow_state(self):
        tools = getMultiAdapter((self.context, self.request), name='plone_tools')
        return tools.portal_workflow.getInfoFor(aq_inner(self.context), 'review_state', None)
                            
    @property
    @memoize
    def is_folderish(self):
        return bool(getattr(aq_base(aq_inner(self.context)), 'isPrincipiaFolderish', False))
            
    @property
    @memoize
    def is_structural_folder(self):
        folderish = self.is_folderish
        context = aq_inner(self.context)
        if not folderish:
            return False
        elif INonStructuralFolder.providedBy(context):
            return False
        elif z2INonStructuralFolder.isImplementedBy(context):
            # BBB: for z2 interface compat
            return False
        else:
            return folderish
        
    @property
    @memoize
    def is_default_page(self):
        context = aq_inner(self.context)
        container = aq_parent(context)
        if not container:
            return False
        view = getMultiAdapter((container, self.request), name='default_page')
        return view.isDefaultPage(context)
    
    @property
    @memoize
    def is_editable(self):
        tools = getMultiAdapter((self.context, self.request), name='plone_tools')
        return tools.portal_membership.checkPermission('Modify portal content', aq_inner(self.context))
    
    @property
    @memoize
    def is_locked(self):
        context = aq_inner(self.context)
        lockable = getattr(context.aq_explicit, 'wl_isLocked', None) is not None
        return lockable and context.wl_isLocked()
                            
    @property
    @memoize
    def actions(self):
        tools = getMultiAdapter((self.context, self.request), name='plone_tools')
        return tools.portal_actions.listFilteredActionsFor(aq_inner(self.context))
        
    @property
    @memoize
    def keyed_actions(self):
        actions = self.actions
        keyed_actions = {}
        for category in actions.keys():
            keyed_actions[category] = {}
            for action in actions[category]:
                id = action.get('id', None)
                if id is not None:
                    keyed_actions[category][id] = action.copy()
        return keyed_actions