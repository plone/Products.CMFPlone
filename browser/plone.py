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
            for name, v in self._data.items():
                state[name] = v
                context.setGlobal(name, v)
            self.request.other['__PloneViewOptimizationRequestCache'] = state
        else:
            for k, v in state.items():
                context.setGlobal(k, v)

    def __init__(self, context, request):
        super(Plone, self).__init__(context, request)

        self._data = {}

        # XXX: Can't store data as attributes directly because it will
        # insert the view into the acquisition chain. Someone should
        # come up with a way to prevent this or get rid of the globals
        # view altogether
        self._data['utool'] = utool = utils.context(self).portal_url
        self._data['portal'] = portal = utool.getPortalObject()
        self._data['portal_object'] =  portal
        self._data['portal_url'] =  utool()
        self._data['mtool'] = mtool = portal.portal_membership
        self._data['gtool'] =  portal.portal_groups or None
        self._data['gdtool'] = portal.portal_groupdata or None
        self._data['atool'] =  portal.portal_actions
        self._data['aitool'] = portal.portal_actionicons or None
        self._data['putils'] = putils = portal.plone_utils
        self._data['wtool'] =  portal.portal_workflow
        self._data['ifacetool'] =  portal.portal_interface or None
        self._data['syntool'] =  portal.portal_syndication
        self._data['portal_title'] = self._data['portal_object'].Title()
        self._data['object_title'] = utils.context(self).pretty_title_or_id()
        self._data['checkPermission'] =  mtool.checkPermission
        self._data['member'] = mtool.getAuthenticatedMember()
        self._data['membersfolder'] =  mtool.getMembersFolder()
        self._data['isAnon'] =  mtool.isAnonymousUser()
        self._data['actions'] = actions = portal.portal_actions.listFilteredActionsFor(utils.context(self))
        self._data['keyed_actions'] =  portal.keyFilteredActions(actions)
        self._data['user_actions'] =  actions['user']
        self._data['workflow_actions'] =  actions['workflow']
        self._data['folder_actions'] =  actions['folder']
        self._data['global_actions'] =  actions['global']
        self._data['portal_tabs'] =  putils.createTopLevelTabs(utils.context(self), actions=actions)
        self._data['wf_state'] =  self._data['wtool'].getInfoFor(utils.context(self),'review_state', None)
        self._data['portal_properties'] =  portal.portal_properties
        self._data['site_properties'] =  self._data['portal_properties'].site_properties
        self._data['ztu'] =  ZTUtils
        self._data['wf_actions'] =  self._data['workflow_actions']
        self._data['isFolderish'] =  utils.context(self).isPrincipiaFolderish
        # i don't know if this is right for 'template_id', but it's more right than what was there before...
        self._data['template_id'] =  self.request.get('template_id', None) or self.request.PUBLISHED.getId() or None
        self._data['slots_mapping'] =  self.request.get('slots_mapping', None) or utils.context(self).prepare_slots() or None
        self._data['Iterator'] =  CMFPlone.IndexIterator
        self._data['tabindex'] =  self._data['Iterator'](pos=30000)
        self._data['here_url'] =  utils.context(self).absolute_url()
        self._data['sl'] =  self._data['slots_mapping']['left']
        self._data['sr'] =  self._data['slots_mapping']['right']
        self._data['hidecolumns'] =  utils.context(self).hide_columns(self._data['sl'],self._data['sr'])
        self._data['default_language'] =  self._data['site_properties'].default_language or None
        self._data['language'] =  self.request.get('language', None) or utils.context(self).Language or self.default_language()
        self._data['is_editable'] =  self._data['checkPermission']('Modify portal content', utils.context(self))
        self._data['isEditable'] =  self._data['is_editable']
        self._data['lockable'] =  hasattr(utils.context(self).aq_inner.aq_explicit, 'wl_isLocked')
        self._data['isLocked'] =  self._data['lockable'] and utils.context(self).wl_isLocked()
        self._data['isRTL'] =  utils.context(self).isRightToLeft(domain='plone')
        self._data['visible_ids'] =  utils.context(self).visibleIdsEnabled() or None
        self._data['current_page_url'] =  utils.context(self).getCurrentUrl() or None
        self._data['view_template_id'] =  utils.context(self).getViewTemplateId() or None
        self._data['isViewTemplate'] =  self._data['template_id']==self._data['view_template_id']
        self._data['normalizeString'] = putils.normalizeString

    def __getattr__(self, key):
        """Override to look in _data first"""

        _marker = []
        value = self.__dict__['_data'].get(key, _marker)
        if value is _marker:
            try:
                value = super(Plone, self).__getattr__(key)
            except AttributeError:
                raise AttributeError, key
        return value
