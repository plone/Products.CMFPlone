from itertools import chain
from Acquisition import aq_inner
from Products.CMFPlone.controlpanel.browser.usergroups import \
    UsersGroupsControlPanelView
from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
from plone.protect import CheckAuthenticator
from zope.component import getMultiAdapter
from zExceptions import Forbidden
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName


class GroupsOverviewControlPanel(UsersGroupsControlPanelView):

    def __call__(self):
        form = self.request.form
        submitted = form.get('form.submitted', False)
        search = form.get('form.button.Search', None) is not None
        findAll = form.get('form.button.FindAll', None) is not None
        self.searchString = not findAll and form.get('searchstring', '') or ''
        self.searchResults = []
        self.newSearch = False

        if search or findAll:
            self.newSearch = True

        if submitted:
            if form.get('form.button.Modify', None) is not None:
                self.manageGroup([group[len('group_'):] for group in self.request.keys() if group.startswith('group_')],
                                 form.get('delete', []))

        # Only search for all ('') if the many_users flag is not set.
        if not(self.many_groups) or bool(self.searchString):
            self.searchResults = self.doSearch(self.searchString)

        return self.index()

    def doSearch(self, searchString):
        """ Search for a group by id or title"""
        acl = getToolByName(self, 'acl_users')
        rolemakers = acl.plugins.listPlugins(IRolesPlugin)

        searchView = getMultiAdapter(
            (aq_inner(self.context), self.request), name='pas_search')

        # First, search for inherited roles assigned to each group.
        # We push this in the request so that IRoles plugins are told provide
        # the roles inherited from the groups to which the principal belongs.
        self.request.set('__ignore_group_roles__', False)
        self.request.set('__ignore_direct_roles__', True)
        inheritance_enabled_groups = searchView.merge(chain(
            *[searchView.searchGroups(**{field: searchString}) for field in ['id', 'title']]), 'id')
        allInheritedRoles = {}
        for group_info in inheritance_enabled_groups:
            groupId = group_info['id']
            group = acl.getGroupById(groupId)
            group_info['title'] = group.getProperty(
                'title', group_info['title'])
            allAssignedRoles = []
            for rolemaker_id, rolemaker in rolemakers:
                # getRolesForPrincipal can return None
                roles = rolemaker.getRolesForPrincipal(group) or ()
                allAssignedRoles.extend(roles)
            allInheritedRoles[groupId] = allAssignedRoles

        # Now, search for all roles explicitly assigned to each group.
        # We push this in the request so that IRoles plugins don't provide
        # the roles inherited from the groups to which the principal belongs.
        self.request.set('__ignore_group_roles__', True)
        self.request.set('__ignore_direct_roles__', False)
        explicit_groups = searchView.merge(chain(
            *[searchView.searchGroups(**{field: searchString}) for field in ['id', 'title']]), 'id')

        # Tack on some extra data, including whether each role is explicitly
        # assigned ('explicit'), inherited ('inherited'), or not assigned at
        # all (None).
        results = []
        for group_info in explicit_groups:
            groupId = group_info['id']
            group = acl.getGroupById(groupId)
            group_info['title'] = group.getProperty(
                'title', group_info['title'])

            explicitlyAssignedRoles = []
            for rolemaker_id, rolemaker in rolemakers:
                # getRolesForPrincipal can return None
                roles = rolemaker.getRolesForPrincipal(group) or ()
                explicitlyAssignedRoles.extend(roles)

            roleList = {}
            for role in self.portal_roles:
                canAssign = group.canAssignRole(role)
                if role == 'Manager' and not self.is_zope_manager:
                    canAssign = False
                roleList[role] = {'canAssign': canAssign,
                                  'explicit': role in explicitlyAssignedRoles,
                                  'inherited': role in allInheritedRoles.get(groupId, [])}

            canDelete = group.canDelete()
            if ('Manager' in explicitlyAssignedRoles or
                    'Manager' in allInheritedRoles.get(groupId, [])):
                if not self.is_zope_manager:
                    canDelete = False

            group_info['roles'] = roleList
            group_info['can_delete'] = canDelete
            results.append(group_info)
        # Sort the groups by title
        sortedResults = searchView.sort(results, 'title')

        # Reset the request variable, just in case.
        self.request.set('__ignore_group_roles__', False)
        return sortedResults

    def manageGroup(self, groups=None, delete=None):
        if groups is None:
            groups = []
        if delete is None:
            delete = []
        CheckAuthenticator(self.request)
        context = aq_inner(self.context)

        groupstool = context.portal_groups
        utils = getToolByName(context, 'plone_utils')
        groupstool = getToolByName(context, 'portal_groups')

        message = _('No changes made.')

        for group in groups:
            roles = [r for r in self.request.form['group_' + group] if r]
            group_obj = groupstool.getGroupById(group)
            current_roles = group_obj.getRoles()
            if not self.is_zope_manager:
                # don't allow adding or removing the Manager role
                if ('Manager' in roles) != ('Manager' in current_roles):
                    raise Forbidden

            groupstool.editGroup(group, roles=roles, groups=())
            message = _('Changes saved.')

        if delete:
            for group_id in delete:
                group = groupstool.getGroupById(group_id)
                if 'Manager' in group.getRoles() and not self.is_zope_manager:
                    raise Forbidden

            groupstool.removeGroups(delete)
            message = _('Group(s) deleted.')

        utils.addPortalMessage(message)
