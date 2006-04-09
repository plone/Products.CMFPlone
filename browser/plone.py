from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFPlone.browser.interfaces import IPlone
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone.interfaces.NonStructuralFolder import INonStructuralFolder
from Products.CMFPlone import utils
from Products.CMFPlone import IndexIterator
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import ListFolderContents
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.permissions import DeleteObjects
from Products.CMFCore.permissions import ReviewPortalContent
from Products.CMFPlone.interfaces.BrowserDefault import IBrowserDefault

from zope.interface import implements
from zope.component import getMultiAdapter
from Products import CMFPlone
import ZTUtils
import sys

_marker = []

# A simple memoize decorator that saves the value of method calls in a mapping
# on the view, don't use this to store anything but python built-ins
def cache_decorator(method):
    key = method.__name__
    def cached_method(self, *args, **kwargs):
        value_cache = getattr(self, '_value_cache', _marker)
        if value_cache is _marker:
            value_cache = self._value_cache = {}
        cached = value_cache.get(key, _marker)
        if cached is not _marker:
            return cached
        else:
            result = method(self, *args, **kwargs)
            value_cache[key] = result
            return result
    return cached_method

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

        state = {}
        self._initializeData()
        for name, v in self._data.items():
            state[name] = v
            context.setGlobal(name, v)

    def __init__(self, context, request):
        super(Plone, self).__init__(context, request)

        self._data = {}

    def _initializeData(self):

        # We don't want to do this in __init__ because the view provides
        # methods which are useful outside of globals.  Also, performing
        # actions during __init__ is dangerous because instances are usually
        # created during traversal, which means authentication hasn't yet
        # happened.
        context = utils.context(self)

        # XXX: Can't store data as attributes directly because it will
        # insert the view into the acquisition chain. Someone should
        # come up with a way to prevent this or get rid of the globals
        # view altogether

        # BBB: utool is deprecated, use portal or portal_url instead
        self._data['utool'] = utool = getToolByName(context, 'portal_url')
        self._data['portal'] = portal = utool.getPortalObject()
        # BBB: portal_object is deprecated use portal instead
        self._data['portal_object'] = portal_object = portal
        self._data['portal_url'] =  utool()
        self._data['mtool'] = mtool = getToolByName(portal, 'portal_membership')
        # BBB: gtool is deprecated because it is only used in sepcialized
        # contexts
        self._data['gtool'] =  getToolByName(portal, 'portal_groups', None)
        # BBB: gdtool is deprecated because it is only used in specialized
        # contexts
        self._data['gdtool'] = getToolByName(portal, 'portal_groupdata', None)
        # BBB: atool is deprecated because it is unsused
        self._data['atool'] = atool = getToolByName(portal, 'portal_actions')
        # BBB: aitool is deprecated because it is unused
        self._data['aitool'] = getToolByName(portal, 'portal_actionicons', None)
        self._data['putils'] = putils = getToolByName(portal, 'plone_utils')
        self._data['wtool'] = wtool = getToolByName(portal, 'portal_workflow')
        self._data['ifacetool'] = getToolByName(portal, 'portal_interface', None)
        self._data['syntool'] = getToolByName(portal, 'portal_syndication')
        self._data['portal_title'] = portal_object.Title()
        self._data['object_title'] = putils.pretty_title_or_id(context)
        self._data['checkPermission'] = checkPermission = mtool.checkPermission
        self._data['member'] = mtool.getAuthenticatedMember()
        self._data['membersfolder'] =  mtool.getMembersFolder()
        self._data['isAnon'] =  mtool.isAnonymousUser()
        self._data['actions'] = actions = atool.listFilteredActionsFor(context)
        self._data['keyed_actions'] =  self.keyFilteredActions(actions)
        self._data['user_actions'] =  actions['user']
        self._data['workflow_actions'] =  actions['workflow']
        self._data['folder_actions'] =  actions['folder']
        self._data['global_actions'] =  actions['global']
        # XXX: This should use the view!
        self._data['portal_tabs'] =  putils.createTopLevelTabs(context,
                                                              actions=actions)
        self._data['wf_state'] =  wtool.getInfoFor(context,'review_state', None)
        self._data['portal_properties'] = props = getToolByName(portal,
                                                          'portal_properties')
        self._data['site_properties'] = site_props = props.site_properties
        self._data['ztu'] =  ZTUtils
        # BBB: wf_actions is deprecated use workflow_actions instead
        self._data['wf_actions'] =  self._data['workflow_actions']
        self._data['isFolderish'] =  context.aq_explicit.isPrincipiaFolderish
        self._data['slots_mapping'] = slots = self.request.get(
                                                            'slots_mapping',
                                                            None) or \
                                              self._prepare_slots() or None
        self._data['sl'] = sl = slots['left']
        self._data['sr'] = sr = slots['right']
        self._data['here_url'] =  context.absolute_url()
        # BBB: hidecolumns is deprecated as it is not needed globally
        self._data['hidecolumns'] =  self.hide_columns(sl, sr)
        self._data['default_language'] = default_language = \
                              site_props.getProperty('default_language', None)
        self._data['language'] =  self.request.get('language', None) or \
                                  context.Language or default_language
        self._data['is_editable'] =  checkPermission('Modify portal content',
                                                     context)
        # BBB: isEditable is deprecated use is_editable instead
        self._data['isEditable'] =  self._data['is_editable']
        lockable = hasattr(aq_inner(context).aq_explicit, 'wl_isLocked')
        # BBB: locakble is deprecated use only isLocked intead, which implies
        # lockable
        self._data['lockable'] = lockable
        self._data['isLocked'] = lockable and context.wl_isLocked()
        self._data['isRTL'] =  self.isRightToLeft(domain='plone')
        self._data['visible_ids'] =  self.visibleIdsEnabled() or None
        self._data['current_page_url'] =  self.getCurrentUrl() or None
        self._data['normalizeString'] = putils.normalizeString
        self._data['toLocalizedTime'] = self.toLocalizedTime
        self._data['isStructuralFolder'] = self.isStructuralFolder()
        self._data['isContextDefaultPage'] = self.isDefaultPageInFolder()

        self._data['navigation_root_url'] = self.navigationRootUrl()
        self._data['Iterator'] = IndexIterator
        self._data['tabindex'] = IndexIterator(pos=30000, mainSlot=False)
        self._data['uniqueItemIndex'] = IndexIterator(pos=0)

    def keyFilteredActions(self, actions=None):
        """ See interface """
        context = utils.context(self)
        if actions is None:
            actions=context.portal_actions.listFilteredActionsFor()

        keyed_actions={}
        for category in actions.keys():
            keyed_actions[category]={}
            for action in actions[category]:
                id=action.get('id',None)
                if id is not None:
                    keyed_actions[category][id]=action.copy()

        return keyed_actions

    def getCurrentUrl(self):
        """ See interface """
        context = utils.context(self)
        request = context.REQUEST
        url = request.get('ACTUAL_URL', request.get('URL', None))
        query = request.get('QUERY_STRING','')
        if query:
            query = '?'+query
        return url+query
    getCurrentUrl = cache_decorator(getCurrentUrl)

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
    visibleIdsEnabled = cache_decorator(visibleIdsEnabled)

    def isRightToLeft(self, domain):
        """ See interface """
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

    def _prepare_slots(self):
        """ Prepares a structure that makes it conveient to determine
            if we want to use-macro or render the path expression.
            The values for the dictioanries is a list of tuples
            that are path expressions and the second value is a
            1 for use-macro, 0 for render path expression.
        """
        context = utils.context(self)
        slots={ 'left':[],
                'right':[],
                'document_actions':[] }

        left_slots=getattr(context,'left_slots', [])
        right_slots=getattr(context,'right_slots', [])
        document_action_slots=getattr(context,'document_action_slots', [])

        #check if the *_slots attributes are callable so that they can be
        # overridden by methods or python scripts

        if callable(left_slots):
            left_slots=left_slots()

        if callable(right_slots):
            right_slots=right_slots()

        if callable(document_action_slots):
            document_action_slots=document_action_slots()

        for slot in left_slots:
            if not slot: continue
            if slot.find('/macros/')!=-1:
                slots['left'].append( (slot, 1) )
            else:
                slots['left'].append( (slot, 0) )

        for slot in right_slots:
            if not slot: continue
            if slot.find('/macros/')!=-1:
                slots['right'].append( (slot, 1) )
            else:
                slots['right'].append( (slot, 0) )

        for slot in document_action_slots:
            if not slot: continue
            if slot.find('/macros/')!=-1:
                slots['document_actions'].append( (slot, 1) )
            else:
                slots['document_actions'].append( (slot, 0) )

        return slots

    def toLocalizedTime(self, time, long_format=None):
        """ See interface """
        context = utils.context(self)
        tool = getToolByName(context, 'translation_service')
        return tool.ulocalized_time(time, long_format, context,
                                    domain='plone')

    def isDefaultPageInFolder(self):
        """ See interface """
        context = utils.context(self)
        request = context.REQUEST
        container = aq_parent(aq_inner((context)))
        if not container:
            return False
        view = getMultiAdapter((container, request), name='default_page')
        view.isDefaultPage(context)
        return view.isDefaultPage(context)
    isDefaultPageInFolder = cache_decorator(isDefaultPageInFolder)

    def isStructuralFolder(self):
        """ See interface """
        context = utils.context(self)
        if not context.isPrincipiaFolderish:
            return False
        #XXX: This should use a z3 interface and directlyProvides
        elif INonStructuralFolder.isImplementedBy(context):
            return False
        else:
            return True
    isStructuralFolder = cache_decorator(isStructuralFolder)

    def navigationRootPath(self):
        context = utils.context(self)
        return getNavigationRoot(context)
    navigationRootPath = cache_decorator(navigationRootPath)

    def navigationRootUrl(self):
        context = utils.context(self)
        portal_url = getToolByName(context, 'portal_url')

        portal = portal_url.getPortalObject()
        portalPath = portal_url.getPortalPath()

        rootPath = getNavigationRoot(context)
        rootSubPath = rootPath[len(portalPath):]

        return portal.absolute_url() + rootSubPath
    navigationRootUrl = cache_decorator(navigationRootUrl)

    def getParentObject(self):
        context = utils.context(self)
        return aq_parent(aq_inner(context))

    def getCurrentFolder(self):
        context = utils.context(self)
        if self.isStructuralFolder() and not self.isDefaultPageInFolder():
            return context
        return self.getParentObject()

    def isFolderOrFolderDefaultPage(self):
        context = utils.context(self)
        if self.isStructuralFolder() or self.isDefaultPageInFolder():
            return True
        return False
    isFolderOrFolderDefaultPage = cache_decorator(isFolderOrFolderDefaultPage)

    def isPortalOrPortalDefaultPage(self):
        context = utils.context(self)
        portal = getToolByName(context, 'portal_url').getPortalObject()
        if aq_base(context) is aq_base(portal) or \
           (aq_base(self.getParentObject()) is aq_base(portal) and
            self.isDefaultPageInFolder()):
            return True
        return False
    isPortalOrPortalDefaultPage = cache_decorator(isPortalOrPortalDefaultPage)

    def getViewTemplateId(self):
        """See interface"""
        context = utils.context(self)
        # XXX: Use z3 interface here
        if IBrowserDefault.isImplementedBy(context):
            try:
                return context.getLayout()
            except AttributeError:
                # Might happen if FTI didn't migrate yet.
                pass

        # Else, if there is a 'folderlisting' action, this will take
        # precedence for folders, so try this, else use the 'view' action.
        action = self._lookupTypeActionTemplate('object/view')

        if not action:
            action = self._lookupTypeActionTemplate('folder/folderlisting')

        return action
    getViewTemplateId = cache_decorator(getViewTemplateId)

    def _lookupTypeActionTemplate(self, actionId):
        context = utils.context(self)
        fti = context.getTypeInfo()
        try:
            # XXX: This isn't quite right since it assumeCs the action starts with ${object_url}
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
    displayContentsTab = cache_decorator(displayContentsTab)
