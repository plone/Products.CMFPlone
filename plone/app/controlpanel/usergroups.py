from Acquisition import aq_inner
from itertools import chain

from zope.interface import Interface
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Bool

from plone.memoize.instance import memoize, clearafter
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot

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

class UsersOverviewControlPanel(ControlPanelView):
    def __call__(self):
        form = self.request.form
        submitted = form.get('form.submitted', False)
        searchTerm = form.get('searchstring', '')

        self.searchResults = []
        if submitted:
            if form.get('form.button.Modify', None) is not None:
                self.manageUser(form.get('users', None),
                                form.get('resetpassword', []),
                                form.get('delete', []))
            self.searchResults = self.doSearch(searchTerm)
                
        return self.index()   
    
    def doSearch(self, searchTerm):
        searchView = getMultiAdapter((aq_inner(self.context), self.request), name='pas_search')
        return searchView.merge(chain(*[searchView.searchUsers(**{field: searchTerm}) for field in ['login', 'fullname']]), 'userid')
        
    def many_users(self):
        pprop = getToolByName(aq_inner(self.context), 'portal_properties')
        return pprop.site_properties.many_users

    def manageUser(self, users=[], resetpassword=[], delete=[]):
        context = aq_inner(self.context)
        acl_users = getToolByName(context, 'acl_users')
        mtool = getToolByName(context, 'portal_membership')
        regtool = getToolByName(context, 'portal_registration')
        mailPassword = regtool.mailPassword
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
                mailPassword(user.id, context.REQUEST)

        if delete:
            # TODO We should eventually have a global switch to determine member area
            # deletion
            mtool.deleteMembers(delete, delete_memberareas=0, delete_localroles=1, REQUEST=context.REQUEST)
        utils.addPortalMessage(_(u'Changes applied.'))
        
    @memoize
    def portal_roles(self):
        pmemb = getToolByName(aq_inner(self.context), 'portal_membership')
        return [r for r in pmemb.getPortalRoles() if r != 'Owner']
        

class GroupsOverviewControlPanel(ControlPanelView):
    def __call__(self):
        self.many_groups = getToolByName(self, 'portal_properties').site_properties.many_groups
        return self.index()
    

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

    form_fields = FormFields(IUserGroupsSettingsSchema)

    label = _("User/Groups settings")
    description = _("User and groups settings for this site.")
    form_name = _("User/Groups settings")
