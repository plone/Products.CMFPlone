from AccessControl import getSecurityManager
from Acquisition import aq_inner
from itertools import chain
from plone.app.registry.browser import controlpanel
from plone.autoform.form import AutoExtensibleForm
from plone.registry.interfaces import IRegistry
from plone.z3cform import layout
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import ISecuritySchema
from Products.CMFPlone.interfaces import IUserGroupsSettingsSchema
from Products.CMFPlone.utils import normalizeString
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form import form
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from ZTUtils import make_query


class UserGroupsSettingsControlPanelForm(controlpanel.RegistryEditForm):
    schema = IUserGroupsSettingsSchema
    schema_prefix = "plone"
    id = "usergroupsettings-control-panel"
    label = _("Users and Groups")
    form_name = _("User/Groups settings")

class UserGroupsSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = UserGroupsSettingsControlPanelForm


class UsersGroupsControlPanelView(BrowserView):
    @property
    def portal_roles(self):
        pmemb = getToolByName(aq_inner(self.context), "portal_membership")
        return [r for r in pmemb.getPortalRoles() if r != "Owner"]

    @property
    def many_users(self):
        registry = getUtility(IRegistry)
        return registry.forInterface(IUserGroupsSettingsSchema, prefix="plone").many_users

    @property
    def many_groups(self):
        registry = getUtility(IRegistry)
        return registry.forInterface(IUserGroupsSettingsSchema, prefix="plone").many_groups

    @property
    def email_as_username(self):
        registry = getUtility(IRegistry)
        return registry.forInterface(ISecuritySchema, prefix="plone").use_email_as_login

    def makeQuery(self, **kw):
        return make_query(**kw)

    def membershipSearch(
        self, searchString="", searchUsers=True, searchGroups=True, ignore=[]
    ):
        """Search for users and/or groups, returning actual member and group items
        Replaces the now-deprecated prefs_user_groups_search.py script"""
        groupResults = userResults = []

        gtool = getToolByName(self, "portal_groups")
        mtool = getToolByName(self, "portal_membership")

        searchView = getMultiAdapter(
            (aq_inner(self.context), self.request), name="pas_search"
        )

        if searchGroups:
            groupResults = searchView.merge(
                chain(
                    *[
                        searchView.searchGroups(**{field: searchString})
                        for field in ["id", "title"]
                    ]
                ),
                "groupid",
            )
            groupResults = [
                gtool.getGroupById(g["id"])
                for g in groupResults
                if g["id"] not in ignore
            ]
            groupResults.sort(
                key=lambda x: x is not None and normalizeString(x.getGroupTitleOrName())
            )

        if searchUsers:
            userResults = searchView.merge(
                chain(
                    *[
                        searchView.searchUsers(**{field: searchString})
                        for field in ["login", "fullname", "email"]
                    ]
                ),
                "userid",
            )
            userResults = [
                mtool.getMemberById(u["id"])
                for u in userResults
                if u["id"] not in ignore
            ]
            userResults.sort(
                key=lambda x: x is not None
                and x.getProperty("fullname") is not None
                and normalizeString(x.getProperty("fullname"))
                or ""
            )

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
            acl = getToolByName(self, "acl_users")
            if acl.canListAllGroups():
                if self.many_groups:
                    return True
        return False

    @property
    def show_users_listing_warning(self):
        if not self.searchString:
            acl = getToolByName(self, "acl_users")
            # XXX Huh? Is canListAllUsers broken?
            if not acl.canListAllUsers():
                if self.many_users:
                    return True
        return False
