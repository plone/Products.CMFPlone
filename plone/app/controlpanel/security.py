import logging
from collections import defaultdict
from zope.cachedescriptors.property import Lazy
from zope.interface import Interface
from zope.component import adapts
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Bool
from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.ActionInformation import Action
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.utils import safe_hasattr
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five import BrowserView
from Products.PlonePAS.interfaces.plugins import IUserManagement

from form import ControlPanelForm

logger = logging.getLogger('plone.app.controlpanel')


class ISecuritySchema(Interface):

    enable_self_reg = Bool(
        title=_(u'Enable self-registration'),
        description=_(u"Allows users to register themselves on the site. If "
                      "not selected, only site managers can add new users."),
        default=False,
        required=False)

    enable_user_pwd_choice = Bool(
        title=_(u'Let users select their own passwords'),
        description=_(u"If not selected, a URL will be generated and "
                      "e-mailed. Users are instructed to follow the link to "
                      "reach a page where they can change their password and "
                      "complete the registration process; this also verifies "
                      "that they have entered a valid email address."),
        default=False,
        required=False)

    enable_user_folders = Bool(
        title=_(u'Enable User Folders'),
        description=_(u"If selected, home folders where users can create "
                      "content will be created when they log in."),
        default=False,
        required=False)

    allow_anon_views_about = Bool(
        title=_(u"Allow anyone to view 'about' information"),
        description=_(u"If not selected only logged-in users will be able to "
                      "view information about who created an item and when it "
                      "was modified."),
        default=False,
        required=False)

    use_email_as_login = Bool(
        title=_(u'Use email address as login name'),
        description=_(u"Allows new  users to login with their email address "
                      "instead of specifying a separate login name. (Existing "
                      "users must go to the @@personal-information page once "
                      "and save it before this setting has effect for them. "
                      "Or use the @@migrate-to-emaillogin page as a site "
                      "admin)"),
        default=False,
        required=False)


class SecurityControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(ISecuritySchema)

    def __init__(self, context):
        super(SecurityControlPanelAdapter, self).__init__(context)
        pprop = getToolByName(context, 'portal_properties')
        self.pmembership = getToolByName(context, 'portal_membership')
        portal_url = getToolByName(context, 'portal_url')
        self.portal = portal_url.getPortalObject()
        self.context = pprop.site_properties

    def get_enable_self_reg(self):
        app_perms = self.portal.rolesOfPermission(permission='Add portal member')
        for appperm in app_perms:
            if appperm['name'] == 'Anonymous' and \
               appperm['selected'] == 'SELECTED':
                return True
        return False

    def set_enable_self_reg(self, value):
        app_perms = self.portal.rolesOfPermission(permission='Add portal member')
        reg_roles = []
        for appperm in app_perms:
            if appperm['selected'] == 'SELECTED':
                reg_roles.append(appperm['name'])
        if value == True and 'Anonymous' not in reg_roles:
            reg_roles.append('Anonymous')
        if value == False and 'Anonymous' in reg_roles:
            reg_roles.remove('Anonymous')

        self.portal.manage_permission('Add portal member', roles=reg_roles,
                                      acquire=0)

    enable_self_reg = property(get_enable_self_reg, set_enable_self_reg)


    def get_enable_user_pwd_choice(self):
        if self.portal.validate_email:
            return False
        else:
            return True

    def set_enable_user_pwd_choice(self, value):
        if value == True:
            self.portal.validate_email = False
        else:
            self.portal.validate_email = True

    enable_user_pwd_choice = property(get_enable_user_pwd_choice,
                                      set_enable_user_pwd_choice)


    def get_enable_user_folders(self):
        return self.pmembership.getMemberareaCreationFlag()

    def set_enable_user_folders(self, value):
        self.pmembership.memberareaCreationFlag = value
        # support the 'my folder' user action #8417
        portal_actions = getToolByName(self.portal, 'portal_actions', None)
        if portal_actions is not None:
            object_category = getattr(portal_actions, 'user', None)
            if value and not safe_hasattr(object_category, 'mystuff'):
                # add action
                self.add_mystuff_action(object_category)
            elif safe_hasattr(object_category, 'mystuff'):
                a = getattr(object_category, 'mystuff')
                a.visible = bool(value)    # show/hide action

    enable_user_folders = property(get_enable_user_folders,
                                   set_enable_user_folders)


    def add_mystuff_action(self, object_category):
        new_action = Action(
            'mystuff',
            title=_(u'My Folder'),
            description='',
            url_expr='string:${portal/portal_membership/getHomeUrl}',
            available_expr='python:(member is not None) and \
                            (portal.portal_membership.getHomeFolder() is not None) ',
            permissions=('View',),
            visible=True,
            i18n_domain='plone')
        object_category._setObject('mystuff', new_action)
        # move action to top, at least before the logout action
        object_category.moveObjectsToTop(('mystuff'))


    def get_allow_anon_views_about(self):
        return self.context.site_properties.allowAnonymousViewAbout

    def set_allow_anon_views_about(self, value):
        self.context.site_properties.allowAnonymousViewAbout = value

    allow_anon_views_about = property(get_allow_anon_views_about,
                                      set_allow_anon_views_about)

    def get_use_email_as_login(self):
        return self.context.use_email_as_login

    def set_use_email_as_login(self, value):
        if value:
            self.context.manage_changeProperties(use_email_as_login=True)
        else:
            self.context.manage_changeProperties(use_email_as_login=False)

    use_email_as_login = property(get_use_email_as_login,
                                  set_use_email_as_login)


class SecurityControlPanel(ControlPanelForm):

    form_fields = FormFields(ISecuritySchema)

    label = _("Security settings")
    description = _("Security settings for this site.")
    form_name = _("Security settings")


class EmailLogin(BrowserView):
    """View to help in migrating to or from using email as login.
    """

    duplicates = []
    switched_to_email = 0
    switched_to_userid = 0

    def __call__(self):
        if self.request.form.get('check'):
            self.duplicates = self.check_duplicates()
        if self.request.form.get('switch_to_email'):
            self.switched_to_email = self.switch_to_email()
        if self.request.form.get('switch_to_userid'):
            self.switched_to_userid = self.switch_to_userid()
        return self.index()

    @property
    def _email_list(self):
        context = aq_inner(self.context)
        pas = getToolByName(context, 'acl_users')
        emails = defaultdict(list)
        for user in pas.getUsers():
            if user is None:
                # Created in the ZMI?
                continue
            email = user.getProperty('email', '')
            if email:
                emails[email].append(user.getUserId())
            else:
                logger.warn("User %s has no email address.", user.getUserId())
        return emails

    @Lazy
    def _plugins(self):
        """Give list of proper IUserManagement plugins that can update a user.
        """
        context = aq_inner(self.context)
        pas = getToolByName(context, 'acl_users')
        plugins = []
        for plugin_id, plugin in pas.plugins.listPlugins(IUserManagement):
            if hasattr(plugin, 'updateUser'):
                plugins.append(plugin)
        if not plugins:
            logger.warn("No proper IUserManagement plugins found.")
        return plugins

    def _update_login(self, userid, login):
        """Update login name of user.
        """
        for plugin in self._plugins:
            try:
                plugin.updateUser(userid, login)
            except KeyError:
                continue
            else:
                logger.info("Gave user id %s login name %s",
                            userid, login)
                return 1
        return 0

    def check_duplicates(self):
        duplicates = []
        for email, userids in self._email_list.items():
            if len(userids) > 1:
                logger.warn("Duplicate accounts for email address %s: %r",
                            email, userids)
                duplicates.append((email, userids))

        return duplicates

    def switch_to_email(self):
        if not self._plugins:
            return 0
        success = 0
        for email, userids in self._email_list.items():
            if len(userids) > 1:
                logger.warn("Not setting login name for accounts with same "
                            "email address %s: %r", email, userids)
                continue
            for userid in userids:
                success += self._update_login(userid, email)
        return success

    def switch_to_userid(self):
        context = aq_inner(self.context)
        pas = getToolByName(context, 'acl_users')
        if not self._plugins:
            return 0
        success = 0
        for user in pas.getUsers():
            if user is None:
                # Created in the ZMI?
                continue
            userid = user.getUserId()
            success += self._update_login(userid, userid)
        return success
