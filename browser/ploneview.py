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
        
        self.tools = getMultiAdapter((context, request), name=u'plone_tools')
        self.portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
        self.context_state = getMultiAdapter((context, request), name=u'plone_context_state')

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

        self._data['utool'] = utool = self.tools.portal_url
        self._data['portal'] = portal = self.portal_state.portal
        self._data['portal_url'] =  self.portal_state.portal_url
        self._data['mtool'] = mtool = self.tools.portal_membership
        self._data['atool'] = atool = self.tools.portal_actions
        self._data['putils'] = putils = self.tools.plone_utils
        self._data['wtool'] = wtool = self.tools.portal_workflow
        self._data['ifacetool'] = self.tools.portal_interface
        self._data['syntool'] = self.tools.portal_syndication
        self._data['portal_title'] = self.portal_state.portal_title
        self._data['object_title'] = self.context_state.object_title
        self._data['checkPermission'] = checkPermission = mtool.checkPermission
        
        # XXX: Disabled for now due to this returning an ImplicitAquisitionWrapper
        # self._data['member'] = self.portal_state.member
        self._data['member'] = self.tools.portal_membership.getAuthenticatedMember()
        
        self._data['membersfolder'] =  mtool.getMembersFolder()
        self._data['isAnon'] =  self.portal_state.anonymous
        self._data['actions'] = actions = (options.get('actions', None) or self.context_state.actions)
        self._data['keyed_actions'] =  self.context_state.keyed_actions
        self._data['user_actions'] =  actions['user']
        self._data['workflow_actions'] =  actions['workflow']
        self._data['folder_actions'] =  actions['folder']
        self._data['global_actions'] =  actions['global']

        portal_tabs_view = getMultiAdapter((context, context.REQUEST), name='portal_tabs_view')
        self._data['portal_tabs'] =  portal_tabs_view.topLevelTabs(actions=actions)

        self._data['wf_state'] =  self.context_state.workflow_state
        self._data['portal_properties'] = props = self.tools.portal_properties
        self._data['site_properties'] = site_props = props.site_properties
        self._data['ztu'] =  ZTUtils
        self._data['isFolderish'] =  self.context_state.is_folderish
        
        # TODO: How should these interact with plone.portlets? Ideally, they'd
        # be obsolete, with a simple "show-column" boolean
        self._data['slots_mapping'] = slots = self._prepare_slots(view)
        self._data['sl'] = sl = slots['left']
        self._data['sr'] = sr = slots['right']
        self._data['hidecolumns'] =  self.hide_columns(sl, sr)
        
        self._data['here_url'] =  self.context_state.object_url
        self._data['default_language'] = self.portal_state.default_language
        self._data['language'] =  self.portal_state.language
        self._data['is_editable'] = self.context_state.is_editable
        self._data['isLocked'] = self.context_state.is_locked
        self._data['isRTL'] =  self.portal_state.is_rtl
        self._data['visible_ids'] =  self.visibleIdsEnabled() or None
        self._data['current_page_url'] =  self.context_state.current_page_url
        self._data['normalizeString'] = putils.normalizeString
        self._data['toLocalizedTime'] = self.toLocalizedTime
        self._data['isStructuralFolder'] = self.context_state.is_structural_folder
        self._data['isContextDefaultPage'] = self.context_state.is_default_page

        self._data['navigation_root_url'] = self.portal_state.navigation_root_url
        self._data['Iterator'] = utils.IndexIterator
        self._data['tabindex'] = utils.IndexIterator(pos=30000, mainSlot=False)
        self._data['uniqueItemIndex'] = utils.IndexIterator(pos=0)

    def keyFilteredActions(self, actions=None):
        """ See interface """
        return self.context_state.keyed_actions

    def getCurrentUrl(self):
        """ See interface """
        return self.context_state.current_page_url

    @memoize
    def visibleIdsEnabled(self):
        """ See interface """
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

    def isRightToLeft(self, domain='plone'):
        """ See interface """
        # Note: Not delegated to @@plone_context_state, because that view
        # does not take into account different domains (it always assumes 'plone')
        context = utils.context(self)
        try:
            from Products.PlacelessTranslationService import isRTL
        except ImportError:
            # This may mean we have an old version of PTS or no PTS at all.
            return 0
        else:
            try:
                return isRTL(context, domain)
            except AttributeError:
                # This may mean that PTS is present but not installed.
                # Can effectively only happen in unit tests.
                return 0

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

    def toLocalizedTime(self, time, long_format=None):
        """ See interface """
        context = utils.context(self)
        tool = getToolByName(context, 'translation_service')
        return tool.ulocalized_time(time, long_format, context,
                                    domain='plone')

    def isDefaultPageInFolder(self):
        """ See interface """
        return self.context_state.is_default_page

    def isStructuralFolder(self):
        """ See interface """
        return self.context_state.is_structural_folder

    def navigationRootPath(self):
        return self.portal_state.navigation_root_path

    def navigationRootUrl(self):
        return self.portal_state.navigation_root_url

    def getParentObject(self):
        return self.context_state.parent

    def getCurrentFolder(self):
        return self.context_state.folder

    def getCurrentFolderUrl(self):
        return self.context_state.folder.absolute_url()

    @memoize
    def getCurrentObjectUrl(self):
        context = utils.context(self)
        if self.isDefaultPageInFolder():
            obj = self.getParentObject()
        else:
            obj = context
        return obj.absolute_url()

    @memoize
    def isFolderOrFolderDefaultPage(self):
        return self.context_state.is_structural_folder or self.context_state.is_default_page

    @memoize
    def isPortalOrPortalDefaultPage(self):
        context = utils.context(self)
        portal = self.portal_state.portal
        if aq_base(context) is aq_base(portal) or \
           (aq_base(self.getParentObject()) is aq_base(portal) and
            self.isDefaultPageInFolder()):
            return True
        return False
        
    @memoize
    def getViewTemplateId(self):
        """See interface"""
        context = utils.context(self)

        browserDefault = IBrowserDefault(context, None)
        if browserDefault is not None:
            try:
                return browserDefault.getLayout()
            except AttributeError:
                # Might happen if FTI didn't migrate yet.
                pass

        # Else, if there is a 'folderlisting' action, this will take
        # precedence for folders, so try this, else use the 'view' action.
        action = self._lookupTypeActionTemplate('object/view')

        if not action:
            action = self._lookupTypeActionTemplate('folder/folderlisting')

        return action

    def _lookupTypeActionTemplate(self, actionId):
        context = utils.context(self)
        fti = context.getTypeInfo()
        try:
            # XXX: This isn't quite right since it assumes the action starts with ${object_url}
            action = fti.getActionInfo(actionId)['url'].split('/')[-1]
        except ValueError:
            # If the action doesn't exist, stop
            return None

        # Try resolving method aliases because we need a real template_id here
        action = fti.queryMethodID(action, default = action, context = context)

        # Strip off leading /
        if action and action[0] == '/':
            action = action[1:]
        return action

    @memoize
    def displayContentsTab(self):
        """See interface"""
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
