from zope.component import getAdapter
from zope.site.hooks import getSite
from zope.component import adapts
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IUserGroupsSettingsSchema
from Products.CMFPlone.interfaces import IPloneSiteRoot


class UserGroupsSettingsControlPanelAdapter(object):

    adapts(IPloneSiteRoot)
    implements(IUserGroupsSettingsSchema)

    def __init__(self, context):
        self.context = context
        self.portal = getSite()
        pprop = getToolByName(context, 'portal_properties')
        self.context = pprop.site_properties

    def get_many_groups(self):
        return self.context.many_groups

    def set_many_groups(self, value):
        self.context.many_groups = value

    many_groups = property(get_many_groups, set_many_groups)

    def get_many_users(self):
        return self.context.many_users

    def set_many_users(self, value):
        self.context.many_users = value

    many_users = property(get_many_users, set_many_users)
