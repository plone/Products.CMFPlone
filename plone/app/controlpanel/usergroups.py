import logging

from Acquisition import aq_inner
from itertools import chain

from zope.interface import Interface
from zope.component import adapts, getAdapter, getMultiAdapter
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Bool
from ZTUtils import make_query

from plone.protect import CheckAuthenticator
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin, IGroupsPlugin

from form import ControlPanelForm, ControlPanelView
from security import ISecuritySchema

logger = logging.getLogger('plone.app.controlpanel')

class IUserGroupsSettingsSchema(Interface):

    many_groups = Bool(title=_(u'Many groups?'),
                       description=_(u"Determines if your Plone is optimized "
                           "for small or large sites. In environments with a "
                           "lot of groups it can be very slow or impossible "
                           "to build a list all groups. This option tunes the "
                           "user interface and behaviour of Plone for this "
                           "case by allowing you to search for groups instead "
                           "of listing all of them."),
                       default=False)

    many_users = Bool(title=_(u'Many users?'),
                      description=_(u"Determines if your Plone is optimized "
                          "for small or large sites. In environments with a "
                          "lot of users it can be very slow or impossible to "
                          "build a list all users. This option tunes the user "
                          "interface and behaviour of Plone for this case by "
                          "allowing you to search for users instead of "
                          "listing all of them."),
                      default=False)

class UserGroupsSettingsControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IUserGroupsSettingsSchema)

    def __init__(self, context):
        super(UserGroupsSettingsControlPanelAdapter, self).__init__(context)
        pprop = getToolByName(context, 'portal_properties')
        self.context = pprop.site_properties

    many_groups = ProxyFieldProperty(IUserGroupsSettingsSchema['many_groups'])
    many_users = ProxyFieldProperty(IUserGroupsSettingsSchema['many_users'])
    
class UserGroupsSettingsControlPanel(ControlPanelForm):

    base_template = ControlPanelForm.template
    template = ZopeTwoPageTemplateFile('usergroupssettings.pt')

    form_fields = FormFields(IUserGroupsSettingsSchema)

    label = _("User/Groups settings")
    description = _("User and groups settings for this site.")
    form_name = _("User/Groups settings")

class UsersGroupsControlPanelView(ControlPanelView):

    @property
    def portal_roles(self):
        pmemb = getToolByName(aq_inner(self.context), 'portal_membership')
        return [r for r in pmemb.getPortalRoles() if r != 'Owner']

    @property
    def many_users(self):
        pprop = getToolByName(aq_inner(self.context), 'portal_properties')
        return pprop.site_properties.many_users

    @property
    def many_groups(self):
        pprop = getToolByName(aq_inner(self.context), 'portal_properties')
        return pprop.site_properties.many_groups

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

        searchView = getMultiAdapter((aq_inner(self.context), self.request), name='pas_search')

        if searchGroups:
            groupResults = searchView.merge(chain(*[searchView.searchGroups(**{field: searchString}) for field in ['id', 'title']]), 'groupid')
            groupResults = [gtool.getGroupById(g['id']) for g in groupResults if g['id'] not in ignore]
            groupResults.sort(key=lambda x: x is not None and x.getGroupTitleOrName().lower())

        if searchUsers:
            userResults = searchView.merge(chain(*[searchView.searchUsers(**{field: searchString}) for field in ['login', 'fullname', 'email']]), 'userid')
            userResults = [mtool.getMemberById(u['id']) for u in userResults if u['id'] not in ignore]
            userResults.sort(key=lambda x: x is not None and x.getProperty('fullname') is not None and x.getProperty('fullname').lower() or '')

        return groupResults + userResults

    def atoi(self, s):
        try:
            return int(s)  
        except ValueError:
            return 0

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

        searchView = getMultiAdapter((aq_inner(self.context), self.request), name='pas_search')

        # First, search for all inherited roles assigned to each group.
        # We push this in the request so that IRoles plugins are told provide
        # the roles inherited from the groups to which the principal belongs.
        self.request.set('__ignore_group_roles__', False)
        self.request.set('__ignore_direct_roles__', True)
        inheritance_enabled_users = searchView.merge(chain(*[searchView.searchUsers(**{field: searchString}) for field in ['login', 'fullname', 'email']]), 'userid')
        allInheritedRoles = {}
        for user_info in inheritance_enabled_users:
            userId = user_info['id']
            user = acl.getUserById(userId)
            # play safe, though this should never happen
            if user is None:
                logger.warn('Skipped user without principal object: %s' % userId)
                continue
            allAssignedRoles = []
            for rolemaker_id, rolemaker in rolemakers:
                allAssignedRoles.extend(rolemaker.getRolesForPrincipal(user))
            allInheritedRoles[userId] = allAssignedRoles

        # We push this in the request such IRoles plugins don't provide
        # the roles from the groups the principal belongs.
        self.request.set('__ignore_group_roles__', True)
        self.request.set('__ignore_direct_roles__', False)
        explicit_users = searchView.merge(chain(*[searchView.searchUsers(**{field: searchString}) for field in ['login', 'fullname', 'email']]), 'userid')

        # Tack on some extra data, including whether each role is explicitly
        # assigned ('explicit'), inherited ('inherited'), or not assigned at all (None).
        results = []
        for user_info in explicit_users:
            userId = user_info['id']
            user = mtool.getMemberById(userId)
            # play safe, though this should never happen
            if user is None:
                logger.warn('Skipped user without principal object: %s' % userId)
                continue
            explicitlyAssignedRoles = []
            for rolemaker_id, rolemaker in rolemakers:
                explicitlyAssignedRoles.extend(rolemaker.getRolesForPrincipal(user))

            roleList = {}
            for role in self.portal_roles:
                roleList[role]={'canAssign': user.canAssignRole(role),
                                'explicit': role in explicitlyAssignedRoles,
                                'inherited': role in allInheritedRoles[userId]}

            user_info['roles'] = roleList
            user_info['fullname'] = user.getProperty('fullname', '')
            user_info['email'] = user.getProperty('email', '')
            user_info['can_delete'] = user.canDelete()
            user_info['can_set_email'] = user.canWriteProperty('email')
            user_info['can_set_password'] = user.canPasswordSet()
            results.append(user_info)

        # Sort the users by fullname
        results.sort(key=lambda x: x is not None and x['fullname'] is not None and x['fullname'].lower() or '')

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

            for user in users:
                # Don't bother if the user will be deleted anyway
                if user.id in delete:
                    continue

                member = mtool.getMemberById(user.id)
                # If email address was changed, set the new one
                if hasattr(user, 'email'):
                    # If the email field was disabled (ie: non-writeable), the
                    # property might not exist.
                    if user.email != member.getProperty('email'):
                        utils.setMemberProperties(member, REQUEST=context.REQUEST, email=user.email)
                        utils.addPortalMessage(_(u'Changes applied.'))

                # If reset password has been checked email user a new password
                pw = None
                if hasattr(user, 'resetpassword'):
                    if not context.unrestrictedTraverse('@@overview-controlpanel').mailhost_warning():
                        pw = regtool.generatePassword()
                    else:
                        utils.addPortalMessage(_(u'No mailhost defined. Unable to reset passwords.'), type='error')

                acl_users.userFolderEditUser(user.id, pw, user.get('roles',[]), member.getDomains(), REQUEST=context.REQUEST)
                if pw:
                    context.REQUEST.form['new_password'] = pw
                    regtool.mailPassword(user.id, context.REQUEST)

            if delete:
                # TODO We should eventually have a global switch to determine member area
                # deletion
                mtool.deleteMembers(delete, delete_memberareas=0, delete_localroles=1, REQUEST=context.REQUEST)
            utils.addPortalMessage(_(u'Changes applied.'))

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

        searchView = getMultiAdapter((aq_inner(self.context), self.request), name='pas_search')

        # First, search for inherited roles assigned to each group.
        # We push this in the request so that IRoles plugins are told provide
        # the roles inherited from the groups to which the principal belongs.
        self.request.set('__ignore_group_roles__', False)
        self.request.set('__ignore_direct_roles__', True)
        inheritance_enabled_groups = searchView.merge(chain(*[searchView.searchGroups(**{field: searchString}) for field in ['id', 'title']]), 'id')
        allInheritedRoles = {}
        for group_info in inheritance_enabled_groups:
            groupId = group_info['id']
            group = acl.getGroupById(groupId)
            allAssignedRoles = []
            for rolemaker_id, rolemaker in rolemakers:
                allAssignedRoles.extend(rolemaker.getRolesForPrincipal(group))
            allInheritedRoles[groupId] = allAssignedRoles

        # Now, search for all roles explicitly assigned to each group.
        # We push this in the request so that IRoles plugins don't provide
        # the roles inherited from the groups to which the principal belongs.
        self.request.set('__ignore_group_roles__', True)
        self.request.set('__ignore_direct_roles__', False)
        explicit_groups = searchView.merge(chain(*[searchView.searchGroups(**{field: searchString}) for field in ['id', 'title']]), 'id')

        # Tack on some extra data, including whether each role is explicitly
        # assigned ('explicit'), inherited ('inherited'), or not assigned at all (None).
        results = []
        for group_info in explicit_groups:
            groupId = group_info['id']
            group = acl.getGroupById(groupId)

            explicitlyAssignedRoles = []
            for rolemaker_id, rolemaker in rolemakers:
                explicitlyAssignedRoles.extend(rolemaker.getRolesForPrincipal(group))

            roleList = {}
            for role in self.portal_roles:
                roleList[role]={'canAssign': group.canAssignRole(role),
                                'explicit': role in explicitlyAssignedRoles,
                                'inherited': role in allInheritedRoles[groupId] }

            group_info['roles'] = roleList
            group_info['can_delete'] = group.canDelete()
            results.append(group_info)
        # Sort the groups by title
        sortedResults = searchView.sort(results, 'title')

        # Reset the request variable, just in case.
        self.request.set('__ignore_group_roles__', False)
        return sortedResults

    def manageGroup(self, groups=[], delete=[]):
        CheckAuthenticator(self.request)
        context = aq_inner(self.context)

        groupstool=context.portal_groups
        utils = getToolByName(context, 'plone_utils')
        groupstool = getToolByName(context, 'portal_groups')

        message = _(u'No changes made.')

        for group in groups:
            roles=[r for r in self.request.form['group_' + group] if r]
            groupstool.editGroup(group, roles=roles, groups=())
            message = _(u'Changes saved.')

        if delete:
            groupstool.removeGroups(delete)
            message=_(u'Group(s) deleted.')

        utils.addPortalMessage(message)

class GroupMembershipControlPanel(UsersGroupsControlPanelView):

    def __call__(self):
        self.groupname = getattr(self.request, 'groupname')
        self.gtool = getToolByName(self, 'portal_groups')
        self.mtool = getToolByName(self, 'portal_membership')
        self.group = self.gtool.getGroupById(self.groupname)
        self.grouptitle = self.group.getGroupTitleOrName() or self.groupname

        self.request.set('grouproles', self.group.getRoles() if self.group else [])

        self.groupquery = self.makeQuery(groupname=self.groupname)
        self.groupkeyquery = self.makeQuery(key=self.groupname)

        form = self.request.form
        submitted = form.get('form.submitted', False)

        self.searchResults = []
        self.searchString = ''
        self.newSearch = False

        if submitted:
            # add/delete before we search so we don't show stale results
            toAdd = form.get('add', [])
            if toAdd:
                for u in toAdd:
                    self.gtool.addPrincipalToGroup(u, self.groupname, self.request)
                self.context.plone_utils.addPortalMessage(_(u'Changes made.'))

            toDelete = form.get('delete', [])
            if toDelete:
                for u in toDelete:
                    self.gtool.removePrincipalFromGroup(u, self.groupname, self.request)
                self.context.plone_utils.addPortalMessage(_(u'Changes made.'))

            search = form.get('form.button.Search', None) is not None
            findAll = form.get('form.button.FindAll', None) is not None and not self.many_users
            self.searchString = not findAll and form.get('searchstring', '') or ''
            if findAll or self.searchString != '':
                self.searchResults = self.getPotentialMembers(self.searchString)

            if search or findAll:
                self.newSearch = True

        self.groupMembers = self.getMembers()

        return self.index()

    def isGroup(self, itemName):
        return self.gtool.isGroup(itemName)

    def getMembers(self):
        searchResults = self.gtool.getGroupMembers(self.groupname)

        groupResults = [self.gtool.getGroupById(m) for m in searchResults]
        groupResults.sort(key=lambda x: x is not None and x.getGroupTitleOrName().lower())

        userResults = [self.mtool.getMemberById(m) for m in searchResults]
        userResults.sort(key=lambda x: x is not None and x.getProperty('fullname') is not None and x.getProperty('fullname').lower() or '')

        mergedResults = groupResults + userResults
        return filter(None, mergedResults)

    def getPotentialMembers(self, searchString):
        ignoredUsersGroups = [x.id for x in self.getMembers() + [self.group,] if x is not None]
        return self.membershipSearch(searchString, ignore=ignoredUsersGroups)

class UserMembershipControlPanel(UsersGroupsControlPanelView):

    def __call__(self):
        self.userid = getattr(self.request, 'userid')
        self.gtool = getToolByName(self, 'portal_groups')
        self.mtool = getToolByName(self, 'portal_membership')
        self.member = self.mtool.getMemberById(self.userid)

        form = self.request.form

        self.searchResults = []
        self.searchString = ''
        self.newSearch = False

        if form.get('form.submitted', False):
            delete = form.get('delete', [])
            if delete:
                for groupname in delete:
                    self.gtool.removePrincipalFromGroup(self.userid, groupname, self.request)
                self.context.plone_utils.addPortalMessage(_(u'Changes made.'))

            add = form.get('add', [])
            if add:
                for groupname in add:
                    self.gtool.addPrincipalToGroup(self.userid, groupname, self.request)
                self.context.plone_utils.addPortalMessage(_(u'Changes made.'))

        search = form.get('form.button.Search', None) is not None
        findAll = form.get('form.button.FindAll', None) is not None and not self.many_groups
        self.searchString = not findAll and form.get('searchstring', '') or ''

        if findAll or not self.many_groups or self.searchString != '':
            self.searchResults = self.getPotentialGroups(self.searchString)

        if search or findAll:
            self.newSearch = True

        self.groups = self.getGroups()
        return self.index()

    def getGroups(self):
        groupResults = [self.gtool.getGroupById(m) for m in self.gtool.getGroupsForPrincipal(self.member)]
        groupResults.sort(key=lambda x: x is not None and x.getGroupTitleOrName().lower())
        return filter(None, groupResults)

    def getPotentialGroups(self, searchString):
        ignoredGroups = [x.id for x in self.getGroups() if x is not None]
        return self.membershipSearch(searchString, searchUsers=False, ignore=ignoredGroups)

