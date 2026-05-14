from plone.base.interfaces import IPloneSiteRoot
from plone.base.interfaces import IUserGroupsSettingsSchema
from plone.registry.interfaces import IRegistry
from zope.component import adapter
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import implementer

import warnings


@adapter(IPloneSiteRoot)
@implementer(IUserGroupsSettingsSchema)
class UserGroupsSettingsControlPanelAdapter:
    def __init__(self, context):
        warnings.warn(
            f"Usage of bbb controlpanel '{self.__class__.__name__}' is deprecated. "
            "Use registry.forInterface(plone.base.interfaces.IUserGroupsSettingsSchema, prefix='plone') instead. "
            "It will be removed in Plone 7.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.context = context
        self.portal = getSite()
        registry = getUtility(IRegistry)
        self.usergroups_settings = registry.forInterface(
            IUserGroupsSettingsSchema, prefix="plone"
        )

    def get_many_groups(self):
        return self.usergroups_settings.many_groups

    def set_many_groups(self, value):
        if value:
            self.usergroups_settings.many_groups = True
        else:
            self.usergroups_settings.many_groups = False

    many_groups = property(get_many_groups, set_many_groups)

    def get_many_users(self):
        return self.usergroups_settings.many_users

    def set_many_users(self, value):
        if value:
            self.usergroups_settings.many_users = True
        else:
            self.usergroups_settings.many_users = False

    many_users = property(get_many_users, set_many_users)
