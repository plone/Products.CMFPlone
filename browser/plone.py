from Products.CMFPlone.interfaces.Plone import IPlone
from zope.interface import implements
from Products.Five import BrowserView
from Products import CMFPlone
import ZTUtils

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class Plone(BrowserView):
   implements(IPlone)
   
   def __init__(self, context, request):
      self.context = context
      self.request = request

   def utool(self):
       return self.context.portal_url

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
       self.context.Title()

   def member(self):
       self.mtool().getAuthenticatedMember()

   def checkPermission(self):
       return self.mtool().checkPermission

   def membersfolder(self):
       return self.mtool().getMembersFolder()

   def isAnon(self):
       return self.mtool().isAnonymousUser()

   def actions(self):
       return self.portal().portal_actions.listFilteredActionsFor(self.context)

   def keyed_actions(self):
       return self.portal().keyFilteredActions(self.actions())

   def user_actions(self):
       return self.actions().user()

   def workflow_actions(self):
       return self.actions().workflow()

   def folder_actions(self):
       return self.actions().folder()

   def global_actions(self):
       return getattr('global', self.actions())()

   def portal_tabs(self):
       return putils.createTopLevelTabs(actions)

   def wf_state(self):
       return wtool.getInfoFor(here,'review_state',None)

   def portal_properties(self):
       return self.portal().portal_properties

   def site_properties(self):
       return self.portal_properties().site_properties

   def ztu(self):
       return ZTUtils

   def actions(self):
       return self.request.get('actions', None) or self.actions()

   def wf_actions(self):
       return self.workflow_actions()

   def isFolderish(self):
       return self.context.isPrincipiaFolderish

   def template_id(self):
       return self.request.get('template_id', None) or self.congext.getId() or None # ?

   def slots_mapping(self):
       return self.request.get('slots_mapping', None) or self.context.prepare_slots() or None

   def Iterator(self):
       return CMFPlone.IndexIterator

   def tabindex(self):
       return Iterator(pos=30000)

   def here_url(self):
       return self.context.absolute_url()

   def sl(self):
       return self.slots_mapping().left()

   def sr(self):
       return self.slots_mapping().right()

   def hidecolumns(self):
       return self.context.hide_columns(sl,sr)

   def default_language(self):
       return self.site_properties().default_language or None

   def language(self):
       return self.request.get('language', None)

   def language(self):
       return self.language() or self.context.Language() or self.default_language()

   def is_editable(self):
       return self.checkPermission('Modify portal content', self.context)

   def isEditable(self):
       return self.is_editable()

   def lockable(self):
       return hasattr(self.context.aq_inner.aq_explicit, 'wl_isLocked')

   def isLocked(self):
       return self.lockable() and self.context.wl_isLocked()

   def isRTL(self):
       return self.context.isRightToLeft(domain='plone')

   def visible_ids(self):
       return self.context.visibleIdsEnabled() or None

   def current_page_url(self):
       return self.context.getCurrentUrl() or None

