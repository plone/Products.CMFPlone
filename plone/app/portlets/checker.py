from zope.interface import implements
from zope.component import adapts

from plone.portlets.interfaces import IPortletAssignmentMapping

from plone.app.portlets.interfaces import IUserPortletAssignmentMapping
from plone.app.portlets.interfaces import IGroupDashboardPortletAssignmentMapping
from plone.app.portlets.interfaces import IPortletPermissionChecker

from AccessControl import getSecurityManager, Unauthorized
from Acquisition import aq_inner


class DefaultPortletPermissionChecker(object):
    implements(IPortletPermissionChecker)
    adapts(IPortletAssignmentMapping)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        sm = getSecurityManager()
        context = aq_inner(self.context)

        # If the user has the global Manage Portlets permission, let them
        # run wild
        if not sm.checkPermission("Portlets: Manage portlets", context):
            raise Unauthorized("You are not allowed to manage portlets")


class UserPortletPermissionChecker(object):
    implements(IPortletPermissionChecker)
    adapts(IUserPortletAssignmentMapping)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        sm = getSecurityManager()
        context = aq_inner(self.context)

        # If the user has the global Manage Portlets permission, let them
        # run wild
        if not sm.checkPermission("Portlets: Manage own portlets", context):
            raise Unauthorized("You are not allowed to manage portlets")

        user_id = sm.getUser().getId()

        if context.__name__ != user_id:
            raise Unauthorized("You are only allowed to manage your own portlets")


class GroupDashboardPortletPermissionChecker(object):
    implements(IPortletPermissionChecker)
    adapts(IGroupDashboardPortletAssignmentMapping)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        sm = getSecurityManager()
        context = aq_inner(self.context)

        if not sm.checkPermission("Portlets: Manage group portlets", context):
            raise Unauthorized("You are not allowed to manage group portlets")
