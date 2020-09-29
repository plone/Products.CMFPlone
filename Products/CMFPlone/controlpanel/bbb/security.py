from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.interfaces import ISecuritySchema
from plone.registry.interfaces import IRegistry
from zope.component import adapts
from zope.component import getUtility
from zope.interface import implementer
from zope.component.hooks import getSite


@implementer(ISecuritySchema)
class SecurityControlPanelAdapter:

    adapts(IPloneSiteRoot)

    def __init__(self, context):
        self.portal = getSite()
        self.pmembership = getToolByName(context, 'portal_membership')
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            ISecuritySchema, prefix="plone")

    def get_enable_self_reg(self):
        return self.settings.enable_self_reg

    def set_enable_self_reg(self, value):
        # additional processing in the event handler
        self.settings.enable_self_reg = value

    enable_self_reg = property(get_enable_self_reg, set_enable_self_reg)

    def get_enable_user_pwd_choice(self):
        return self.settings.enable_user_pwd_choice

    def set_enable_user_pwd_choice(self, value):
        self.settings.enable_user_pwd_choice = value

    enable_user_pwd_choice = property(get_enable_user_pwd_choice,
                                      set_enable_user_pwd_choice)

    def get_enable_user_folders(self):
        return self.settings.enable_user_folders

    def set_enable_user_folders(self, value):
        # additional processing in the event handler
        self.settings.enable_user_folders = value

    enable_user_folders = property(get_enable_user_folders,
                                   set_enable_user_folders)

    def get_allow_anon_views_about(self):
        return self.settings.allow_anon_views_about

    def set_allow_anon_views_about(self, value):
        self.settings.allow_anon_views_about = value

    allow_anon_views_about = property(get_allow_anon_views_about,
                                      set_allow_anon_views_about)

    def get_use_email_as_login(self):
        return self.settings.use_email_as_login

    def set_use_email_as_login(self, value):
        # additional processing in the event handler
        self.settings.use_email_as_login = value

    use_email_as_login = property(get_use_email_as_login,
                                  set_use_email_as_login)

    def get_use_uuid_as_userid(self):
        return self.settings.use_uuid_as_userid

    def set_use_uuid_as_userid(self, value):
        self.settings.use_uuid_as_userid = value

    use_uuid_as_userid = property(get_use_uuid_as_userid,
                                  set_use_uuid_as_userid)
