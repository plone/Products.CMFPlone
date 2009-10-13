from Acquisition import aq_inner
from itertools import chain

from zope.interface import Interface
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Bool

from plone.memoize.instance import memoize, clearafter
from plone.protect import CheckAuthenticator
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from form import ControlPanelForm, ControlPanelView


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


class UsersOverviewControlPanel(ControlPanelView):

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
        return searchView.merge(chain(*[searchView.searchUsers(**{field: searchString}) for field in ['login', 'fullname', 'email']]), 'userid')

    @property
    def many_users(self):
        pprop = getToolByName(aq_inner(self.context), 'portal_properties')
        return pprop.site_properties.many_users

    def manageUser(self, users=[], resetpassword=[], delete=[]):
        CheckAuthenticator(self.request)
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

    @property
    def portal_roles(self):
        pmemb = getToolByName(aq_inner(self.context), 'portal_membership')
        return [r for r in pmemb.getPortalRoles() if r != 'Owner']


class GroupsOverviewControlPanel(ControlPanelView):

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
        searchView = getMultiAdapter((aq_inner(self.context), self.request), name='pas_search')
        return searchView.merge(chain(*[searchView.searchGroups(**{field: searchString}) for field in ['id', 'title']]), 'id')

    def manageGroup(self, groups=[], delete=[]):
        CheckAuthenticator(self.request)
        context = aq_inner(self.context)

        groupstool=context.portal_groups
        utils = getToolByName(context, 'plone_utils')
        groupstool = getToolByName(context, 'portal_groups')

        message = _(u'No changes done.')

        for group in groups:
            roles=[r for r in self.request.form['group_' + group] if r]
            groupstool.editGroup(group, roles=roles, groups=())
            message = _(u'Changes saved.')

        if delete:
            groupstool.removeGroups(delete)
            message=_(u'Group(s) deleted.')

        utils.addPortalMessage(message)
        #return state

    @property
    def portal_roles(self):
        pmemb = getToolByName(aq_inner(self.context), 'portal_membership')
        return [r for r in pmemb.getPortalRoles() if r != 'Owner']

    @property
    def many_groups(self):
        pprop = getToolByName(aq_inner(self.context), 'portal_properties')
        return pprop.site_properties.many_groups 
