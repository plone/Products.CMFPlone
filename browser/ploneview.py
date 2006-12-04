from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.permissions import DeleteObjects
from Products.CMFCore.permissions import ListFolderContents
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import ReviewPortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import IPlone
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone.interfaces import IBrowserDefault
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.CMFPlone.interfaces.NonStructuralFolder import INonStructuralFolder\
     as z2INonStructuralFolder
from Products.CMFPlone.browser.interfaces import IContentIcon

from zope.interface import implements
from zope.component import getMultiAdapter, queryMultiAdapter, getUtility

import ZTUtils
import sys

from plone.memoize.view import memoize
from plone.portlets.interfaces import IPortletManager, IPortletManagerRenderer

# @@ deprecate import from this location?
IndexIterator = utils.IndexIterator

_marker = []

import zope.deferredimport
zope.deferredimport.deprecated(
    "It has been replaced by plone.memoize.instance.memoize. This alias will " 
    "be gone in Plone 4.0.",
    cache_decorator = 'plone.memoize.instance.memoize',
    )

class Plone(utils.BrowserView):
    implements(IPlone)

    def globalize(self):
        """
        Pure optimization hack, globalizes entire view for speed. Yes
        it's evil, but this hack will eventually be removed after
        globals are officially deprecated.

        YOU CAN ONLY CALL THIS METHOD FROM A PAGE TEMPLATE AND EVEN
        THEN IT MIGHT DESTROY YOU!
        """
        context = sys._getframe(2).f_locals['econtext']
        # Some of the original global_defines used 'options' to get parameters
        # passed in through the template call, so we need this to support
        # products which may have used this little hack
        options = context.vars.get('options',{})
        view = context.vars.get('view', {})

        state = {}
        self._initializeData(options=options, view=view)
        for name, v in self._data.items():
            state[name] = v
            context.setGlobal(name, v)

    def __init__(self, context, request):
        super(Plone, self).__init__(context, request)
        self._data = {}

    def _initializeData(self, options=None, view=None):
        # We don't want to do this in __init__ because the view provides
        # methods which are useful outside of globals.  Also, performing
        # actions during __init__ is dangerous because instances are usually
        # created during traversal, which means authentication hasn't yet
        # happened.
        context = utils.context(self)
        if options is None:
            options = {}

        # XXX: Can't store data as attributes directly because it will
        # insert the view into the acquisition chain. Someone should
        # come up with a way to prevent this or get rid of the globals
        # view altogether

        tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        context_state = getMultiAdapter((context, self.request), name=u'plone_context_state')

        self._data['utool'] = utool = tools.url()
        self._data['portal'] = portal = portal_state.portal()
        self._data['portal_url'] =  portal_state.portal_url()
        self._data['mtool'] = mtool = tools.membership()
        self._data['atool'] = atool = tools.actions()
        self._data['putils'] = putils = getToolByName(context, 'plone_utils')
        self._data['wtool'] = wtool = tools.workflow()
        self._data['ifacetool'] = getToolByName(context, 'portal_interface')
        self._data['syntool'] = tools.syndication()
        self._data['portal_title'] = portal_state.portal_title()
        self._data['object_title'] = context_state.object_title()
        self._data['checkPermission'] = checkPermission = mtool.checkPermission
        self._data['member'] = portal_state.member()
        self._data['membersfolder'] =  mtool.getMembersFolder()
        self._data['isAnon'] =  portal_state.anonymous()
        self._data['actions'] = actions = (options.get('actions', None) or context_state.actions())
        self._data['keyed_actions'] =  context_state.keyed_actions()
        self._data['user_actions'] =  actions['user']
        self._data['workflow_actions'] =  actions['workflow']
        self._data['folder_actions'] =  actions['folder']
        self._data['global_actions'] =  actions['global']

        portal_tabs_view = getMultiAdapter((context, context.REQUEST), name='portal_tabs_view')
        self._data['portal_tabs'] =  portal_tabs_view.topLevelTabs(actions=actions)

        self._data['wf_state'] =  context_state.workflow_state()
        self._data['portal_properties'] = props = tools.properties()
        self._data['site_properties'] = site_props = props.site_properties
        self._data['ztu'] =  ZTUtils
        self._data['isFolderish'] =  context_state.is_folderish()
        
        # TODO: How should these interact with plone.portlets? Ideally, they'd
        # be obsolete, with a simple "show-column" boolean
        self._data['slots_mapping'] = slots = self._prepare_slots(view)
        self._data['sl'] = sl = slots['left']
        self._data['sr'] = sr = slots['right']
        self._data['hidecolumns'] =  self.hide_columns(sl, sr)
        
        self._data['here_url'] =  context_state.object_url()
        self._data['default_language'] = portal_state.default_language()
        self._data['language'] =  portal_state.language()
        self._data['is_editable'] = context_state.is_editable()
        self._data['isLocked'] = context_state.is_locked()
        self._data['isRTL'] =  portal_state.is_rtl()
        self._data['visible_ids'] =  self.visibleIdsEnabled() or None
        self._data['current_page_url'] =  context_state.current_page_url()
        self._data['normalizeString'] = putils.normalizeString
        self._data['toLocalizedTime'] = self.toLocalizedTime
        self._data['isStructuralFolder'] = context_state.is_structural_folder()
        self._data['isContextDefaultPage'] = context_state.is_default_page()

        self._data['navigation_root_url'] = portal_state.navigation_root_url()
        self._data['Iterator'] = utils.IndexIterator
        self._data['tabindex'] = utils.IndexIterator(pos=30000, mainSlot=False)
        self._data['uniqueItemIndex'] = utils.IndexIterator(pos=0)

    # XXX: This is lame
    def hide_columns(self, column_left, column_right):
        """ See interface """

        if column_right==[] and column_left==[]:
            return "visualColumnHideOneTwo"
        if column_right!=[]and column_left==[]:
            return "visualColumnHideOne"
        if column_right==[]and column_left!=[]:
            return "visualColumnHideTwo"
        return "visualColumnHideNone"

    # Utility methods
    
    def toLocalizedTime(self, time, long_format=None):
        """Convert time to localized time
        """
        context = utils.context(self)
        tool = getToolByName(context, 'translation_service')
        return tool.ulocalized_time(time, long_format, context,
                                    domain='plone')
    
    @memoize
    def visibleIdsEnabled(self):
        """Determine if visible ids are enabled
        """
        context = utils.context(self)
        props = getToolByName(context, 'portal_properties').site_properties
        if not props.getProperty('visible_ids', False):
            return False

        pm=context.portal_membership
        if pm.isAnonymousUser():
            return False

        user = pm.getAuthenticatedMember()
        if user is not None:
            return user.getProperty('visible_ids', False)
        return False
    
    @memoize
    def displayContentsTab(self):
        """Whether or not the contents tabs should be displayed
        """
        context = utils.context(self)
        modification_permissions = (ModifyPortalContent,
                                    AddPortalContent,
                                    DeleteObjects,
                                    ReviewPortalContent)

        contents_object = context
        # If this object is the parent folder's default page, then the
        # folder_contents action is for the parent, we check permissions
        # there. Otherwise, if the object is not folderish, we don not display
        # the tab.
        if self.isDefaultPageInFolder():
            contents_object = self.getCurrentFolder()
        elif not self.isStructuralFolder():
            return 0

        # If this is not a structural folder, stop.
        plone_view = getMultiAdapter((contents_object, self.request),
                                     name='plone')
        if not plone_view.isStructuralFolder():
            return 0

        show = 0
        # We only want to show the 'contents' action under the following
        # conditions:
        # - If you have permission to list the contents of the relavant
        #   object, and you can DO SOMETHING in a folder_contents view. i.e.
        #   Copy or Move, or Modify portal content, Add portal content,
        #   or Delete objects.

        # Require 'List folder contents' on the current object
        if _checkPermission(ListFolderContents, contents_object):
            # If any modifications are allowed on object show the tab.
            for permission in modification_permissions:
                if _checkPermission(permission, contents_object):
                    show = 1
                    break

        return show

    def getIcon(self, item):
        """Returns an item with informations necessary to render an icon.
           The item parameter can either be a catalog brain, or a content
           object."""
        context = utils.context(self)
        icon = getMultiAdapter((context, self.request, item), IContentIcon)
        return icon

    # Deprecated in favour of the @@plone_context_state and @@plone_portal_state views

    def keyFilteredActions(self, actions=None):
        context_state = getMultiAdapter((utils.context(self), self.request), name=u'plone_context_state')
        return context_state.keyed_actions()

    def getCurrentUrl(self):
        context_state = getMultiAdapter((utils.context(self), self.request), name=u'plone_context_state')
        return context_state.current_page_url()

    def isRightToLeft(self, domain='plone'):
        portal_state = getMultiAdapter((utils.context(self), self.request), name=u'plone_portal_state')
        return portal_state.is_rtl(domain)

    def isDefaultPageInFolder(self):
        context_state = getMultiAdapter((utils.context(self), self.request), name=u'plone_context_state')
        return context_state.is_default_page()

    def isStructuralFolder(self):
        context_state = getMultiAdapter((utils.context(self), self.request), name=u'plone_context_state')
        return context_state.is_structural_folder()

    def navigationRootPath(self):
        portal_state = getMultiAdapter((utils.context(self), self.request), name=u'plone_portal_state')
        return portal_state.navigation_root_path()

    def navigationRootUrl(self):
        portal_state = getMultiAdapter((utils.context(self), self.request), name=u'plone_portal_state')
        return portal_state.navigation_root_url()

    def getParentObject(self):
        context_state = getMultiAdapter((utils.context(self), self.request), name=u'plone_context_state')
        return context_state.parent()

    def getCurrentFolder(self):
        context_state = getMultiAdapter((utils.context(self), self.request), name=u'plone_context_state')
        return context_state.folder()

    def getCurrentFolderUrl(self):
        context_state = getMultiAdapter((utils.context(self), self.request), name=u'plone_context_state')
        return context_state.folder().absolute_url()

    @memoize
    def getCurrentObjectUrl(self):
        context_state = getMultiAdapter((utils.context(self), self.request), name=u'plone_context_state')
        return context_state.canonical_object_url()

    @memoize
    def isFolderOrFolderDefaultPage(self):
        context_state = getMultiAdapter((utils.context(self), self.request), name=u'plone_context_state')
        return context_state.is_structural_folder() or context_state.is_default_page()

    @memoize
    def isPortalOrPortalDefaultPage(self):
        context_state = getMultiAdapter((utils.context(self), self.request), name=u'plone_context_state')
        return context_state.is_portal_root()
        
    @memoize
    def getViewTemplateId(self):
        context_state = getMultiAdapter((utils.context(self), self.request), name=u'plone_context_state')
        return context_state.view_template_id()
        
    # Helper methods
    def _prepare_slots(self, view=None):
        """XXX: This is a silly attempt at BBB - the only purpose of this
        function is to return [] or [1] (non-empty) for each slot 'left' and
        'right', whether or not that column should be rendered.
        """
        
        context = utils.context(self)
        slots = {'left' : [1], 'right' : [1]}

        if view is None:
            view = self

        left = getUtility(IPortletManager, name='plone.leftcolumn')
        right = getUtility(IPortletManager, name='plone.rightcolumn')
        
        leftRenderer = queryMultiAdapter((context, self.request, view, left), IPortletManagerRenderer)
        rightRenderer = queryMultiAdapter((context, self.request, view, right), IPortletManagerRenderer)
        
        if leftRenderer is None:
            leftRenderer = getMultiAdapter((context, self.request, self, left), IPortletManagerRenderer)
            
        if rightRenderer is None:
            rightRenderer = getMultiAdapter((context, self.request, self, right), IPortletManagerRenderer)
        
        if not leftRenderer.visible:
            slots['left'] = []
        if not rightRenderer.visible:
            slots['right'] = []
            
        return slots