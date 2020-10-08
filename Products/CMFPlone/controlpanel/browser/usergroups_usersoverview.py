from Acquisition import aq_inner
from zExceptions import Forbidden
from itertools import chain

from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
from zope.component import getUtility
from plone.protect import CheckAuthenticator
from zope.component import getMultiAdapter
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.utils import normalizeString
from Products.CMFPlone.controlpanel.browser.usergroups import \
    UsersGroupsControlPanelView

import logging

logger = logging.getLogger('Products.CMFPlone')


class UsersOverviewControlPanel(UsersGroupsControlPanelView):

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
                self.manageUser(form.get('users', None),
                                form.get('resetpassword', []),
                                form.get('delete', []))

        # Only search for all ('') if the many_users flag is not set.
        if not(self.many_users) or bool(self.searchString):
            self.searchResults = self.doSearch(self.searchString)

        return self.index()

    def doSearch(self, searchString):
        acl = getToolByName(self, 'acl_users')
        rolemakers = acl.plugins.listPlugins(IRolesPlugin)

        mtool = getToolByName(self, 'portal_membership')

        searchView = getMultiAdapter((
            aq_inner(self.context),
            self.request
        ), name='pas_search')

        # First, search for all inherited roles assigned to each group.
        # We push this in the request so that IRoles plugins are told provide
        # the roles inherited from the groups to which the principal belongs.
        self.request.set('__ignore_group_roles__', False)
        self.request.set('__ignore_direct_roles__', True)
        inheritance_enabled_users = searchView.merge(
            chain(*[searchView.searchUsers(**{field: searchString}) for field in ['login', 'fullname', 'email']]), 'userid')
        allInheritedRoles = {}
        for user_info in inheritance_enabled_users:
            userId = user_info['id']
            user = acl.getUserById(userId)
            # play safe, though this should never happen
            if user is None:
                logger.warning(
                    'Skipped user without principal object: %s' % userId)
                continue
            allAssignedRoles = []
            for rolemaker_id, rolemaker in rolemakers:
                allAssignedRoles.extend(rolemaker.getRolesForPrincipal(user))
            allInheritedRoles[userId] = allAssignedRoles

        # We push this in the request such IRoles plugins don't provide
        # the roles from the groups the principal belongs.
        self.request.set('__ignore_group_roles__', True)
        self.request.set('__ignore_direct_roles__', False)
        explicit_users = searchView.merge(
            chain(*[searchView.searchUsers(**{field: searchString})
                    for field in ['login', 'fullname', 'email']]), 'userid'
        )

        # Tack on some extra data, including whether each role is explicitly
        # assigned ('explicit'), inherited ('inherited'), or not assigned at
        # all (None).
        results = []
        for user_info in explicit_users:
            userId = user_info['id']
            user = mtool.getMemberById(userId)
            # play safe, though this should never happen
            if user is None:
                logger.warning(
                    'Skipped user without principal object: %s' % userId)
                continue
            explicitlyAssignedRoles = []
            for rolemaker_id, rolemaker in rolemakers:
                explicitlyAssignedRoles.extend(
                    rolemaker.getRolesForPrincipal(user))

            roleList = {}
            for role in self.portal_roles:
                canAssign = user.canAssignRole(role)
                if role == 'Manager' and not self.is_zope_manager:
                    canAssign = False
                roleList[role] = {'canAssign': canAssign,
                                  'explicit': role in explicitlyAssignedRoles,
                                  'inherited': role in allInheritedRoles.get(userId, ())}

            canDelete = user.canDelete()
            canPasswordSet = user.canPasswordSet()
            if roleList['Manager']['explicit'] or roleList['Manager']['inherited']:
                if not self.is_zope_manager:
                    canDelete = False
                    canPasswordSet = False

            user_info['roles'] = roleList
            user_info['fullname'] = user.getProperty('fullname', '')
            user_info['email'] = user.getProperty('email', '')
            user_info['can_delete'] = canDelete
            user_info['can_set_email'] = user.canWriteProperty('email')
            user_info['can_set_password'] = canPasswordSet
            results.append(user_info)

        # Sort the users by fullname
        results.sort(key=lambda x: x is not None and x[
                     'fullname'] is not None and normalizeString(x['fullname']) or '')

        # Reset the request variable, just in case.
        self.request.set('__ignore_group_roles__', False)
        return results

    def manageUser(self, users=[], resetpassword=[], delete=[]):
        CheckAuthenticator(self.request)

        if users:
            context = aq_inner(self.context)
            acl_users = getToolByName(context, 'acl_users')
            mtool = getToolByName(context, 'portal_membership')
            regtool = getToolByName(context, 'portal_registration')

            utils = getToolByName(context, 'plone_utils')

            users_with_reset_passwords = []

            for user in users:
                # Don't bother if the user will be deleted anyway
                if user.id in delete:
                    continue

                member = mtool.getMemberById(user.id)
                current_roles = member.getRoles()
                # If email address was changed, set the new one
                if hasattr(user, 'email'):
                    # If the email field was disabled (ie: non-writeable), the
                    # property might not exist.
                    if user.email != member.getProperty('email'):
                        utils.setMemberProperties(
                            member, REQUEST=context.REQUEST, email=user.email)
                        utils.addPortalMessage(_('Changes applied.'))

                # If reset password has been checked email user a new password
                pw = None
                if hasattr(user, 'resetpassword'):
                    if 'Manager' in current_roles and not self.is_zope_manager:
                        raise Forbidden
                    if not context.unrestrictedTraverse('@@overview-controlpanel').mailhost_warning():
                        pw = regtool.generatePassword()
                    else:
                        utils.addPortalMessage(
                            _('No mailhost defined. Unable to reset passwords.'), type='error')

                roles = user.get('roles', [])
                if not self.is_zope_manager:
                    # don't allow adding or removing the Manager role
                    if ('Manager' in roles) != ('Manager' in current_roles):
                        raise Forbidden

                acl_users.userFolderEditUser(
                    user.id, pw, roles, member.getDomains(), REQUEST=context.REQUEST)
                if pw:
                    context.REQUEST.form['new_password'] = pw
                    regtool.mailPassword(user.id, context.REQUEST)
                    users_with_reset_passwords.append(user.id)

            if delete:
                self.deleteMembers(delete)
            if users_with_reset_passwords:
                reset_passwords_message = _(
                    "reset_passwords_msg",
                    default="The following users have been sent an e-mail with link to reset their password: ${user_ids}",
                    mapping={
                        "user_ids": ', '.join(users_with_reset_passwords),
                    },
                )
                utils.addPortalMessage(reset_passwords_message)
            utils.addPortalMessage(_('Changes applied.'))

    def deleteMembers(self, member_ids):
        # this method exists to bypass the 'Manage Users' permission check
        # in the CMF member tool's version
        context = aq_inner(self.context)
        mtool = getToolByName(self.context, 'portal_membership')

        # Delete members in acl_users.
        acl_users = context.acl_users
        if isinstance(member_ids, str):
            member_ids = (member_ids,)
        member_ids = list(member_ids)
        for member_id in member_ids[:]:
            member = mtool.getMemberById(member_id)
            if member is None:
                member_ids.remove(member_id)
            else:
                if not member.canDelete():
                    raise Forbidden
                if 'Manager' in member.getRoles() and not self.is_zope_manager:
                    raise Forbidden
        try:
            acl_users.userFolderDelUsers(member_ids)
        except (AttributeError, NotImplementedError):
            raise NotImplementedError('The underlying User Folder '
                                      'doesn\'t support deleting members.')

        # Delete member data in portal_memberdata.
        mdtool = getToolByName(context, 'portal_memberdata', None)
        if mdtool is not None:
            for member_id in member_ids:
                mdtool.deleteMemberData(member_id)

        # Delete members' local roles.
        mtool.deleteLocalRoles(
            getUtility(ISiteRoot),
            member_ids,
            reindex=1,
            recursive=1
        )
