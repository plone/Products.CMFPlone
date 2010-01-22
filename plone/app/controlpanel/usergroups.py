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

from form import ControlPanelForm, ControlPanelView
from security import ISecuritySchema

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

class UsersOverviewControlPanel(UsersGroupsControlPanelView):

    def __call__(self):

        form = self.request.form
        submitted = form.get('form.submitted', False)
        findAll = form.get('form.button.FindAll', None) is not None
        self.searchString = not findAll and form.get('searchstring', '') or ''
        self.searchResults = []
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
        # We push this in the request such IRoles plugins don't provide
        # the roles from the groups the principal belongs.
        self.request.set('__ignore_group_roles__', True)
        searchView = getMultiAdapter((aq_inner(self.context), self.request), name='pas_search')
        self.request.set('__ignore_group_roles__', False)
        return searchView.merge(chain(*[searchView.searchUsers(**{field: searchString}) for field in ['login', 'fullname', 'email']]), 'userid')

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
        findAll = form.get('form.button.FindAll', None) is not None
        self.searchString = not findAll and form.get('searchstring', '') or ''
        self.searchResults = []
        if submitted:
            if form.get('form.button.Modify', None) is not None:
                self.manageGroup([group[len('group_'):] for group in self.request.keys() if group.startswith('group_')],
                                 form.get('delete', []))

        # Only search for all ('') if the many_users flag is not set.
        if not(self.many_groups) or bool(self.searchString):
            self.searchResults = self.doSearch(self.searchString)

        return self.index()

    def doSearch(self, searchString):
        # We push this in the request such IRoles plugins don't provide
        # the roles from the groups the principal belongs.
        self.request.set('__ignore_group_roles__', True)
        searchView = getMultiAdapter((aq_inner(self.context), self.request), name='pas_search')
        results = searchView.merge(chain(*[searchView.searchGroups(**{field: searchString}) for field in ['id', 'title']]), 'id')
        sortedResults = searchView.sort(results, 'title')
        self.request.set('__ignore_group_roles__', False)
        
        return results
        
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
        
        if submitted:
            findAll = form.get('form.button.FindAll', None) is not None and not self.many_users
            self.searchString = not findAll and form.get('searchstring', '') or ''
            self.searchResults = self.doSearch(self.searchString)
        
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

        self.groupMembers = self.getMembers
        
        return self.index()

    def isGroup(self, itemName):
        return self.gtool.isGroup(itemName)

    def getMembers(self):
        searchResults = self.gtool.getGroupMembers(self.groupname)

        groupResults = [self.gtool.getGroupById(m) for m in searchResults]
        groupResults.sort(key=lambda x: x is not None and x.getGroupTitleOrName().lower())

        userResults = [self.mtool.getMemberById(m) for m in searchResults]
        userResults.sort(key=lambda x: x is not None and x.getProperty('fullname').lower())
        
        mergedResults = groupResults + userResults
        filter(None, mergedResults)
        return mergedResults

    def doSearch(self, searchString):
        findAll = 'form.button.FindAll' in self.request.keys()
        ignoredUsersGroups = self.getMembers() + [self.group,]
        return (searchString or findAll) and self.context.prefs_user_group_search(searchString, 'all', ignore=ignoredUsersGroups) or []
        