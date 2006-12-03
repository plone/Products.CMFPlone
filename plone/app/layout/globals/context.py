from zope.interface import implements
from zope.component import getMultiAdapter
from plone.memoize.view import memoize

from Aquisition import aq_inner, aq_parent
from Products.Five.browser import BrowserView

from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.CMFPlone.interfaces.NonStructuralFolder import INonStructuralFolder \
     as z2INonStructuralFolder

class ContextState(BrowserView):
    """Information about the state of the current context
    """
    
    @property
    @memoize
    def current_page_url(self):
        url = self.request.get('ACTUAL_URL', self.request.get('URL', None))
        query = self.request.get('QUERY_STRING','')
        if query:
            query = '?' + query
        return url + query
        
    @property
    @memoize
    def object_url(self):
        return self.context.absolute_url()
        
    @property
    @memoize
    def object_title(self):
        tools = getMultiAdapter((self.context, self.request), name='plone_tools')
        return tools.plone_utils.pretty_title_or_id(self.context)
        
    @property
    @memoize
    def workflow_state(self):
        tools = getMultiAdapter((self.context, self.request), name='plone_tools')
        return tools.portal_workflows.getInfoFor(self.context, 'review_state', None)
                            
    @property
    @memoize
    def is_structural_folder(self):
        folderish = bool(getattr(aq_base(self.context), 'isPrincipiaFolderish', False))
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
        container = aq_parent(aq_inner((self.context)))
        if not container:
            return False
        view = getMultiAdapter((container, self.request), name='default_page')
        return view.isDefaultPage(context)
    
    @property
    @memoize
    def is_editable(self):
        tools = getMultiAdapter((self.context, self.request), name='plone_tools')
        return tools.portal_membership.checkPermission('Modify portal content', self.context)
                            
    @property
    @memoize
    def actions(self):
        tools = getMultiAdapter((self.context, self.request), name='plone_tools')
        return tools.portal_actions.listFilteredActionsFor(context)
        
    @property
    @memoize
    def keyed_actions(self):
        tools = getMultiAdapter((self.context, self.request), name='plone_tools')
        return tools.portal_actions.keyFilteredActions(context)