from Products.CMFPlone.browser.interfaces import IPloneGlobals
from Products.CMFPlone import utils

from zope.interface import implements
from Products.Five import BrowserView
from Products import CMFPlone
import ZTUtils, sys

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.PageTemplates.Expressions import getEngine
from ZPublisher.BeforeTraverse import registerBeforeTraverse

class PloneGlobals(utils.BrowserView):
    implements(IPloneGlobals)

    _globals = ('utool', 'portal', 'portal_object', 'portal_url',
                'mtool', 'gtool', 'gdtool', 'atool', 'aitool', 'putils',
                'wtool', 'ifacetool', 'syntool', 'portal_title', 'object_title',
                'member', 'checkPermission', 'membersfolder', 'isAnon', 'actions',
                'keyed_actions', 'user_actions', 'workflow_actions', 'folder_actions',
                'global_actions', 'portal_tabs', 'wf_state', 'portal_properties',
                'site_properties', 'ztu', 'wf_actions', 'isFolderish', 'template_id',
                'slots_mapping', 'Iterator', 'tabindex', 'here_url', 'sl', 'sr', 'hidecolumns',
                'default_language', 'language', 'is_editable', 'isEditable', 'lockable',
                'isLocked', 'isRTL', 'visible_ids', 'current_page_url')

    def globals(self):
        """
        Pure optimization hack, globalizes entire view for speed. Yes
        it's evil, but this hack will eventually be removed after
        globals are officially deprecated.
        """
        context = sys._getframe(2).f_locals['econtext']
        for name in self._globals:
            context.setGlobal(name, getattr(self, name)())

    def utool(self):
        return utils.context(self).portal_url

    def portal(self):
        return self.utool().getPortalObject()

    def portal_object(self):
        return self.portal()

    def portal_url(self):
        return self.utool()()

    def mtool(self):
        return self.portal().portal_membership

    def gtool(self):
        return self.portal().portal_groups or None

    def gdtool(self):
        return self.portal().portal_groupdata or None

    def atool(self):
        return self.portal().portal_actions

    def aitool(self):
        return self.portal().portal_actionicons or None

    def putils(self):
        return self.portal().plone_utils

    def wtool(self):
        return self.portal().portal_workflow

    def ifacetool(self):
        return self.portal().portal_interface or None

    def syntool(self):
        return self.portal().portal_syndication

    def portal_title(self):
        self.portal_object().Title()

    def object_title(self):
        utils.context(self).Title()

    def member(self):
        self.mtool().getAuthenticatedMember()

    def checkPermission(self):
        return self.mtool().checkPermission

    def membersfolder(self):
        return self.mtool().getMembersFolder()

    def isAnon(self):
        return self.mtool().isAnonymousUser()

    def actions(self):
        return self.portal().portal_actions.listFilteredActionsFor(utils.context(self))

    def keyed_actions(self):
        return self.portal().keyFilteredActions(self.actions())

    def user_actions(self):
        return self.actions()['user']

    def workflow_actions(self):
        return self.actions()['workflow']

    def folder_actions(self):
        return self.actions()['folder']

    def global_actions(self):
        return self.actions()['global']

    def portal_tabs(self):
        return self.putils().createTopLevelTabs(self.actions())

    def wf_state(self):
        return self.wtool().getInfoFor(utils.context(self),'review_state', None)

    def portal_properties(self):
        return self.portal().portal_properties

    def site_properties(self):
        return self.portal_properties().site_properties

    def ztu(self):
        return ZTUtils

    def wf_actions(self):
        return self.workflow_actions()

    def isFolderish(self):
        return utils.context(self).isPrincipiaFolderish

    def template_id(self):
        return self.request.get('template_id', None) or utils.context(self).getId() or None # ?

    def slots_mapping(self):
        return self.request.get('slots_mapping', None) or utils.context(self).prepare_slots() or None

    def Iterator(self):
        return CMFPlone.IndexIterator

    def tabindex(self):
        return self.Iterator()(pos=30000)

    def here_url(self):
        return utils.context(self).absolute_url()

    def sl(self):
        return self.slots_mapping()['left']

    def sr(self):
        return self.slots_mapping()['right']

    def hidecolumns(self):
        return utils.context(self).hide_columns(self.sl(),self.sr())

    def default_language(self):
        return self.site_properties().default_language or None

    def language(self):
        return self.request.get('language', None) or utils.context(self).Language() or self.default_language()

    def is_editable(self):
        return self.checkPermission()('Modify portal content', utils.context(self))

    def isEditable(self):
        return self.is_editable()

    def lockable(self):
        return hasattr(utils.context(self).aq_inner.aq_explicit, 'wl_isLocked')

    def isLocked(self):
        return self.lockable() and utils.context(self).wl_isLocked()

    def isRTL(self):
        return utils.context(self).isRightToLeft(domain='plone')

    def visible_ids(self):
        return utils.context(self).visibleIdsEnabled() or None

    def current_page_url(self):
        return utils.context(self).getCurrentUrl() or None

