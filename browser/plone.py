from Products.CMFPlone.browser.interfaces import IPlone
from Products.CMFPlone import utils

from zope.interface import implements
from Products.Five import BrowserView
from Products import CMFPlone
import ZTUtils, sys

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.PageTemplates.Expressions import getEngine
from ZPublisher.BeforeTraverse import registerBeforeTraverse

class Plone(utils.BrowserView):
    implements(IPlone)

    _globals = (
        'utool', 'portal', 'portal_object', 'portal_url',
        'mtool', 'gtool', 'gdtool', 'atool', 'aitool', 'putils',
        'wtool', 'ifacetool', 'syntool', 'portal_title', 'object_title',
        'member', 'checkPermission', 'membersfolder', 'isAnon', 'actions',
        'keyed_actions', 'user_actions', 'workflow_actions', 'folder_actions',
        'global_actions', 'portal_tabs', 'wf_state', 'portal_properties',
        'site_properties', 'ztu', 'wf_actions', 'isFolderish', 'template_id',
        'slots_mapping', 'Iterator', 'tabindex', 'here_url', 'sl', 'sr',
        'hidecolumns', 'default_language', 'language', 'is_editable',
        'isEditable', 'lockable', 'isLocked', 'isRTL', 'visible_ids',
        'current_page_url', 'view_template_id', 'isViewTemplate',
        'normalizeString')

    def globals(self):
        """
        Pure optimization hack, globalizes entire view for speed. Yes
        it's evil, but this hack will eventually be removed after
        globals are officially deprecated.

        YOU CAN ONLY CALL THIS METHOD FROM A PAGE TEMPLATE AND EVEN
        THEN IT MIGHT DESTROY YOU!
        """

        state = self.request.other.get('__PloneViewOptimizationRequestCache', None)
        context = sys._getframe(2).f_locals['econtext']
        
        if state is None:
            state = {}
            for name in self._globals:
                v = getattr(self, name)
                state[name] = v
                context.setGlobal(name, v)
            self.request.other['__PloneViewOptimizationRequestCache'] = state
        else:
            for k, v in state.items():
                context.setGlobal(k, v)

    def __init__(self, context, request):
        super(Plone, self).__init__(context, request)

        self.utool = utool = utils.context(self).portal_url
        self.portal = portal = utool.getPortalObject()
        self.portal_object =  portal
        self.portal_url =  utool()
        self.mtool = mtool = portal.portal_membership
        self.gtool =  portal.portal_groups or None
        self.gdtool = portal.portal_groupdata or None
        self.atool =  portal.portal_actions
        self.aitool = portal.portal_actionicons or None
        self.putils = putils = portal.plone_utils
        self.wtool =  portal.portal_workflow
        self.ifacetool =  portal.portal_interface or None
        self.syntool =  portal.portal_syndication
        self.portal_title = self.portal_object.Title()
        self.object_title = utils.context(self).pretty_title_or_id()
        self.member = mtool.getAuthenticatedMember()
        self.checkPermission =  mtool.checkPermission
        self.membersfolder =  mtool.getMembersFolder()
        self.isAnon =  mtool.isAnonymousUser()
        self.actions = actions = portal.portal_actions.listFilteredActionsFor(utils.context(self))
        self.keyed_actions =  portal.keyFilteredActions(actions)
        self.user_actions =  actions['user']
        self.workflow_actions =  actions['workflow']
        self.folder_actions =  actions['folder']
        self.global_actions =  actions['global']
        self.portal_tabs =  putils.createTopLevelTabs(utils.context(self), actions=actions)
        self.wf_state =  self.wtool.getInfoFor(utils.context(self),'review_state', None)
        self.portal_properties =  portal.portal_properties
        self.site_properties =  self.portal_properties.site_properties
        self.ztu =  ZTUtils
        self.wf_actions =  self.workflow_actions
        self.isFolderish =  utils.context(self).isPrincipiaFolderish
        self.template_id =  self.request.get('template_id', None) or utils.context(self).getId() or None # ?
        self.slots_mapping =  self.request.get('slots_mapping', None) or utils.context(self).prepare_slots() or None
        self.Iterator =  CMFPlone.IndexIterator
        self.tabindex =  self.Iterator(pos=30000)
        self.here_url =  utils.context(self).absolute_url()
        self.sl =  self.slots_mapping['left']
        self.sr =  self.slots_mapping['right']
        self.hidecolumns =  utils.context(self).hide_columns(self.sl,self.sr)
        self.default_language =  self.site_properties.default_language or None
        self.language =  self.request.get('language', None) or utils.context(self).Language or self.default_language()
        self.is_editable =  self.checkPermission('Modify portal content', utils.context(self))
        self.isEditable =  self.is_editable
        self.lockable =  hasattr(utils.context(self).aq_inner.aq_explicit, 'wl_isLocked')
        self.isLocked =  self.lockable and utils.context(self).wl_isLocked()
        self.isRTL =  utils.context(self).isRightToLeft(domain='plone')
        self.visible_ids =  utils.context(self).visibleIdsEnabled() or None
        self.current_page_url =  utils.context(self).getCurrentUrl() or None
        self.view_template_id =  utils.context(self).getViewTemplateId() or None
        self.isViewTemplate =  self.template_id==self.view_template_id
        self.normalizeString = putils.normalizeString

