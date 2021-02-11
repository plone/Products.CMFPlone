from Products.CMFCore.permissions import ManagePortal
from ZTUtils import make_query
from itertools import chain
from Acquisition import aq_inner
from Products.CMFPlone.utils import normalizeString
from zope.component import getAdapter
from Products.CMFPlone.interfaces import ISecuritySchema
from zope.component import getMultiAdapter
from AccessControl import getSecurityManager
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.z3cform import layout
from plone.autoform.form import AutoExtensibleForm
from Products.CMFPlone import PloneMessageFactory as _
from z3c.form import form

from Products.CMFPlone.interfaces import IUserGroupsSettingsSchema
from z3c.form import button


class UserGroupsSettingsControlPanel(AutoExtensibleForm, form.EditForm):
    schema = IUserGroupsSettingsSchema
    id = "usergroupsettings-control-panel"
    label = _("Users and Groups")
    form_name = _("User/Groups settings")
    control_panel_view = "usergroups-controlpanel"

    @button.buttonAndHandler(_('label_save', default="Save"), name='save')
    def handleApply(self, action):
        super().handleApply(self, action)

    def updateActions(self):
        super().updateActions()
        if self.actions and 'save' in self.actions:
            self.actions['save'].addClass('btn-primary')


class ControlPanelFormWrapper(layout.FormWrapper):
    """Use this form as the plone.z3cform layout wrapper to get the control
    panel layout.
    """

    index = ViewPageTemplateFile('controlpanel_usergroups_layout.pt')


UserGroupsSettingsPanelView = layout.wrap_form(
    UserGroupsSettingsControlPanel, ControlPanelFormWrapper
)


class UsersGroupsControlPanelView(BrowserView):

    @property
    def portal_roles(self):
        pmemb = getToolByName(aq_inner(self.context), 'portal_membership')
        return [r for r in pmemb.getPortalRoles() if r != 'Owner']

    @property
    def many_users(self):
        return getAdapter(aq_inner(self.context), IUserGroupsSettingsSchema).many_users

    @property
    def many_groups(self):
        return getAdapter(aq_inner(self.context), IUserGroupsSettingsSchema).many_groups

    @property
    def email_as_username(self):
        return getAdapter(aq_inner(self.context), ISecuritySchema).get_use_email_as_login()

    def makeQuery(self, **kw):
        return make_query(**kw)

    def membershipSearch(self, searchString='', searchUsers=True, searchGroups=True, ignore=[]):
        """Search for users and/or groups, returning actual member and group items
           Replaces the now-deprecated prefs_user_groups_search.py script"""
        groupResults = userResults = []

        gtool = getToolByName(self, 'portal_groups')
        mtool = getToolByName(self, 'portal_membership')

        searchView = getMultiAdapter(
            (aq_inner(self.context), self.request), name='pas_search')

        if searchGroups:
            groupResults = searchView.merge(chain(
                *[searchView.searchGroups(**{field: searchString}) for field in ['id', 'title']]), 'groupid')
            groupResults = [gtool.getGroupById(g['id']) for g in groupResults if g[
                'id'] not in ignore]
            groupResults.sort(key=lambda x: x is not None and normalizeString(
                x.getGroupTitleOrName()))

        if searchUsers:
            userResults = searchView.merge(chain(*[searchView.searchUsers(
                **{field: searchString}) for field in ['login', 'fullname', 'email']]), 'userid')
            userResults = [mtool.getMemberById(u['id']) for u in userResults if u[
                'id'] not in ignore]
            userResults.sort(key=lambda x: x is not None and x.getProperty(
                'fullname') is not None and normalizeString(x.getProperty('fullname')) or '')

        return groupResults + userResults

    def atoi(self, s):
        try:
            return int(s)
        except ValueError:
            return 0

    @property
    def is_zope_manager(self):
        return getSecurityManager().checkPermission(ManagePortal, self.context)

    # The next two class methods implement the following truth table:
    #
    # MANY USERS/GROUPS SEARCHING       CAN LIST USERS/GROUPS   RESULT
    # False             False           False                   Lists unavailable
    # False             False           True                    Show all
    # False             True            False                   Show matching
    # False             True            True                    Show matching
    # True              False           False                   Too many to list
    # True              False           True                    Lists unavailable
    # True              True            False                   Show matching
    # True              True            True                    Show matching

    # TODO: Maybe have these methods return a text message (instead of a bool)
    # corresponding to the actual result, e.g. "Too many to list", "Lists
    # unavailable"

    @property
    def show_group_listing_warning(self):
        if not self.searchString:
            acl = getToolByName(self, 'acl_users')
            if acl.canListAllGroups():
                if self.many_groups:
                    return True
        return False

    @property
    def show_users_listing_warning(self):
        if not self.searchString:
            acl = getToolByName(self, 'acl_users')
            # XXX Huh? Is canListAllUsers broken?
            if not acl.canListAllUsers():
                if self.many_users:
                    return True
        return False
