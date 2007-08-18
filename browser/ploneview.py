from urllib import unquote

from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.permissions import DeleteObjects
from Products.CMFCore.permissions import ListFolderContents
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import ReviewPortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import IPlone
from Products.CMFPlone.interfaces import ITranslationServiceTool

from zope.deprecation import deprecate, deprecated
from zope.interface import implements, alsoProvides
from zope.component import getMultiAdapter, queryMultiAdapter, getUtility

import ZTUtils
import sys

from plone.memoize.view import memoize
from plone.portlets.interfaces import IPortletManager, IPortletManagerRenderer

from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.icons.interfaces import IContentIcon

from plone.app.content.browser.folderfactories import _allowedTypes

deprecated(
    ('IndexIterator'),
    "This reference to IndexIterator will be removed in Plone 3.5. Please "
    "import it from Products.CMFPlone.utils instead.")

IndexIterator = utils.IndexIterator

_marker = []

import zope.deferredimport
zope.deferredimport.deprecated(
    "It has been replaced by plone.memoize.instance.memoize. This alias will " 
    "be removed in Plone 3.5.",
    cache_decorator = 'plone.memoize.instance:memoize',
    )

class Plone(BrowserView):
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
        view = context.vars.get('view', None)
        template = context.vars.get('template', None)

        state = {}
        self._initializeData(options=options, view=view, template=template)
        for name, v in self._data.items():
            state[name] = v
            context.setGlobal(name, v)

    def __init__(self, context, request):
        super(Plone, self).__init__(context, request)
        self._data = {}

    def _initializeData(self, options=None, view=None, template=None):
        # We don't want to do this in __init__ because the view provides
        # methods which are useful outside of globals.  Also, performing
        # actions during __init__ is dangerous because instances are usually
        # created during traversal, which means authentication hasn't yet
        # happened.
        context = aq_inner(self.context)
        if options is None:
            options = {}
        if view is None:
            view = self

        show_portlets = not options.get('no_portlets', False)
        def_actions = options.get('actions', None)

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
        self._data['putils'] = putils = getToolByName(context, "plone_utils")
        self._data['acl_users'] = getToolByName(context, 'acl_users')
        self._data['wtool'] = wtool = tools.workflow()
        self._data['ifacetool'] = tools.interface()
        self._data['syntool'] = tools.syndication()
        self._data['portal_title'] = portal_state.portal_title()
        self._data['object_title'] = context_state.object_title()
        self._data['checkPermission'] = checkPermission = mtool.checkPermission
        self._data['member'] = portal_state.member()
        self._data['membersfolder'] =  mtool.getMembersFolder()
        self._data['isAnon'] =  portal_state.anonymous()
        self._data['actions'] = actions = def_actions or context_state.actions()
        self._data['keyed_actions'] =  def_actions or context_state.keyed_actions()
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
        
        self._data['sl'] = have_left_portlets = show_portlets and self.have_portlets('plone.leftcolumn', view)
        self._data['sr'] = have_right_portlets = show_portlets and self.have_portlets('plone.rightcolumn', view)
        self._data['hidecolumns'] =  self.hide_columns(have_left_portlets, have_right_portlets)
        
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
        self._data['uniqueItemIndex'] = utils.RealIndexIterator(pos=0)

        template_id = options.get('template_id', None)
        if template_id is None and template is not None:
            template_id = template.getId()
        self._data['template_id'] = template_id
        
        isViewTemplate = context_state.is_view_template()
        if isViewTemplate and not IViewView.providedBy(view):
            # Mark the view as being "the" view
            alsoProvides(view, IViewView)
            
        self._data['isViewTemplate'] = isViewTemplate

    # XXX: This is lame
    def hide_columns(self, column_left, column_right):
        if not column_right and not column_left:
            return "visualColumnHideOneTwo"
        if column_right and not column_left:
            return "visualColumnHideOne"
        if not column_right and column_left:
            return "visualColumnHideTwo"
        return "visualColumnHideNone"

    # Utility methods
    
    def toLocalizedTime(self, time, long_format=None):
        """Convert time to localized time
        """
        context = aq_inner(self.context)
        util = getToolByName(context, 'translation_service')
        return util.ulocalized_time(time, long_format, context=context,
                                    domain='plonelocales', request=self.request)
    
    @memoize
    def visibleIdsEnabled(self):
        """Determine if visible ids are enabled
        """
        context = aq_inner(self.context)
        props = getToolByName(context, "portal_properties").site_properties
        if not props.getProperty('visible_ids', False):
            return False

        pm = getToolByName(context, "portal_membership")
        if pm.isAnonymousUser():
            return False

        user = pm.getAuthenticatedMember()
        if user is not None:
            return user.getProperty('visible_ids', False)
        return False
    
    @memoize
    def prepareObjectTabs(self, default_tab='view', sort_first=frozenset(['folderContents'])):
        """Prepare the object tabs by determining their order and working
        out which tab is selected. Used in global_contentviews.pt
        """
        context = aq_inner(self.context)
        context_url = context.absolute_url()
        context_fti = context.getTypeInfo()
        
        site_properties = getToolByName(context, "portal_properties").site_properties

        context_state = getMultiAdapter((context, self.request), name=u'plone_context_state')
        actions = context_state.actions()

        action_list = []
        if context_state.is_structural_folder():
            action_list = actions['folder'] + actions['object']
        else:
            action_list = actions['object']

        first_tabs = []
        tabs = []
        
        found_selected = False
        fallback_action = None

        request_url = self.request['ACTUAL_URL']
        request_url_path = request_url[len(context_url):]
        
        if request_url_path.startswith('/'):
            request_url_path = request_url_path[1:]

        for action in action_list:
            
            item = {'title'    : action['title'],
                    'id'       : action['id'],
                    'url'      : '',
                    'selected' : False}

            action_url = action['url'].strip()
            if action_url.startswith('http') or action_url.startswith('javascript'):
                item['url'] = action_url
            else:
                item['url'] = '%s/%s'%(context_url, action_url)

            action_method = item['url'].split('/')[-1]

            # Action method may be a method alias: Attempt to resolve to a template.
            action_method = context_fti.queryMethodID(action_method, default=action_method)
            if action_method:
                request_action = unquote(request_url_path)
                request_action = context_fti.queryMethodID(request_action, default=request_action)
    
                if action_method == request_action:
                    item['selected'] = True
                    found_selected = True

            current_id = item['id']
            if current_id == default_tab:
                fallback_action = item

            if current_id in sort_first:
                first_tabs.append(item)
            else:
                tabs.append(item)

        if not found_selected and fallback_action is not None:
            fallback_action['selected'] = True

        return first_tabs + tabs

    # XXX: This can't be request-memoized, because it won't necessarily remain
    # valid across traversals. For example, you may get tabs on an error 
    # message. :)
    # 
    # @memoize
    def showEditableBorder(self):
        """Determine if the editable border should be shown
        """
        request = self.request
        
        if request.has_key('disable_border'): #short circuit
            return False
        if request.has_key('enable_border'): #short circuit
            return True
        
        context = aq_inner(self.context)
        
        portal_membership = getToolByName(context, 'portal_membership')
        checkPerm = portal_membership.checkPermission

        if checkPerm('Modify portal content', context) or \
               checkPerm('Add portal content', context)  or \
               checkPerm('Review portal content', context):
            return True

        if portal_membership.isAnonymousUser():
            return False

        context_state = getMultiAdapter((context, request), name="plone_context_state")
        actions = context_state.actions()
            
        if actions.get('workflow', ()):
            return True

        if actions.get('batch', []):
            return True
            
        for action in actions.get('object', []):
            if action.get('id', '') != 'view':
                return True

        template_id = self._data.get('template_id', None)
        if template_id is None and 'PUBLISHED' in request:
            if hasattr(request['PUBLISHED'], 'getId'):
                template_id=request['PUBLISHED'].getId()

        idActions = {}
        for obj in actions.get('object', ()) + actions.get('folder', ()):
            idActions[obj.get('id', '')] = 1

        if idActions.has_key('edit'):
            if (idActions.has_key(template_id) or \
                template_id in ['synPropertiesForm', 'folder_contents', 'folder_listing']) :
                return True

        # Check to see if the user is able to add content or change workflow state
        if _allowedTypes(request, context):
            return True

        return False
    
    @memoize
    def displayContentsTab(self):
        """Whether or not the contents tabs should be displayed
        """
        context = aq_inner(self.context)
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

    @memoize
    def icons_visible(self):
        context = aq_inner(self.context)
        membership = getToolByName(context, "portal_membership")
        properties = getToolByName(context, "portal_properties")

        site_properties = getattr(properties, 'site_properties')
        icon_visibility = site_properties.getProperty('icon_visibility', 'enabled')

        if icon_visibility == 'enabled':
            return True
        elif icon_visibility == 'authenticated' and not membership.isAnonymousUser():
            return True
        else:
            return False

    def getIcon(self, item):
        """Returns an object which implements the IContentIcon interface and
           provides the informations necessary to render an icon.
           The item parameter needs to be adaptable to IContentIcon.
           Icons can be disabled globally or just for anonymous users with
           the icon_visibility property in site_properties."""
        context = aq_inner(self.context)
        if not self.icons_visible():
            icon = getMultiAdapter((context, self.request, None), IContentIcon)
        else:
            icon = getMultiAdapter((context, self.request, item), IContentIcon)
        return icon

    def normalizeString(self, text, relaxed=False):
        """Normalizes a title to an id.
        """
        return utils.normalizeString(text, context=self, relaxed=relaxed)

    def cropText(self, text, length, ellipsis='...'):
        """Crop text on a word boundary
        """
        converted = False
        if not isinstance(text, unicode):
            encoding = utils.getSiteEncoding(aq_inner(self.context))
            text = unicode(text, encoding)
            converted = True
        if len(text)>length:
            text = text[:length]
            l = text.rfind(' ')
            if l > length/2:
                text = text[:l+1]
            text += ellipsis
        if converted:
            # encode back from unicode
            text = text.encode(encoding)
        return text

    # Deprecated in favour of the @@plone_context_state and @@plone_portal_state views

    @deprecate("The keyFilteredActions method of the Plone view has been "
               "deprecated and will be removed in Plone 3.5. Use the "
               "keyed_actions method of the plone_context_state adapter "
               "instead.")
    def keyFilteredActions(self, actions=None):
        context_state = getMultiAdapter((aq_inner(self.context), self.request), name=u'plone_context_state')
        return context_state.keyed_actions()

    def getCurrentUrl(self):
        context_state = getMultiAdapter((aq_inner(self.context), self.request), name=u'plone_context_state')
        return context_state.current_page_url()

    @deprecate("The isRightToLeft method of the Plone view has been "
               "deprecated and will be removed in Plone 3.5. Use the "
               "is_rtl method of the plone_portal_state adapter instead.")
    def isRightToLeft(self, domain='plone'):
        portal_state = getMultiAdapter((aq_inner(self.context), self.request), name=u'plone_portal_state')
        return portal_state.is_rtl()

    def isDefaultPageInFolder(self):
        context_state = getMultiAdapter((aq_inner(self.context), self.request), name=u'plone_context_state')
        return context_state.is_default_page()

    def isStructuralFolder(self):
        context_state = getMultiAdapter((aq_inner(self.context), self.request), name=u'plone_context_state')
        return context_state.is_structural_folder()

    def navigationRootPath(self):
        portal_state = getMultiAdapter((aq_inner(self.context), self.request), name=u'plone_portal_state')
        return portal_state.navigation_root_path()

    def navigationRootUrl(self):
        portal_state = getMultiAdapter((aq_inner(self.context), self.request), name=u'plone_portal_state')
        return portal_state.navigation_root_url()

    def getParentObject(self):
        context_state = getMultiAdapter((aq_inner(self.context), self.request), name=u'plone_context_state')
        return context_state.parent()

    def getCurrentFolder(self):
        context_state = getMultiAdapter((aq_inner(self.context), self.request), name=u'plone_context_state')
        return context_state.folder()

    def getCurrentFolderUrl(self):
        context_state = getMultiAdapter((aq_inner(self.context), self.request), name=u'plone_context_state')
        return context_state.folder().absolute_url()

    @memoize
    def getCurrentObjectUrl(self):
        context_state = getMultiAdapter((aq_inner(self.context), self.request), name=u'plone_context_state')
        return context_state.canonical_object_url()

    @memoize
    def isFolderOrFolderDefaultPage(self):
        context_state = getMultiAdapter((aq_inner(self.context), self.request), name=u'plone_context_state')
        return context_state.is_structural_folder() or context_state.is_default_page()

    @memoize
    def isPortalOrPortalDefaultPage(self):
        context_state = getMultiAdapter((aq_inner(self.context), self.request), name=u'plone_context_state')
        return context_state.is_portal_root()
        
    @memoize
    def getViewTemplateId(self):
        context_state = getMultiAdapter((aq_inner(self.context), self.request), name=u'plone_context_state')
        return context_state.view_template_id()

    # Helper methods
    def have_portlets(self, manager_name, view=None):
        """Determine whether a column should be shown.
        The left column is called plone.leftcolumn; the right column is called
        plone.rightcolumn. Custom skins may have more portlet managers defined
        (see portlets.xml).
        """
        
        context = aq_inner(self.context)
        if view is None:
            view = self

        manager = getUtility(IPortletManager, name=manager_name)
        renderer = queryMultiAdapter((context, self.request, view, manager), IPortletManagerRenderer)
        if renderer is None:
            renderer = getMultiAdapter((context, self.request, self, manager), IPortletManagerRenderer)

        return renderer.visible
