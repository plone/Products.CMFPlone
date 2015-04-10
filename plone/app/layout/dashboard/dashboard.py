from zope.component import getUtility
from zope import interface

from AccessControl import getSecurityManager
from Products.Five.browser import BrowserView

from plone.portlets.interfaces import IPortletManager
from plone.portlets.constants import USER_CATEGORY, GROUP_CATEGORY

from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone import PloneMessageFactory as _
from plone.protect.authenticator import createToken


class IDashboard(interface.Interface):
    """the dashboard display columns of portlet to the loggedin user"""


class DashboardView(BrowserView):
    """Power the dashboard
    """
    interface.implements(IDashboard)

    def __call__(self):
        self.request.set('disable_border',1)
        self.request.set('disable_plone.leftcolumn',1)
        self.request.set('disable_plone.rightcolumn',1)
        if self.can_edit() and self.empty():
            message = _(u"info_empty_dashboard",
                    default=u"Your dashboard is currently empty. Click the"
                             " <em>edit</em> tab to assign some personal"
                             " portlets.")
            IStatusMessage(self.request).add(message)
        return self.index()

    @property
    def auth_token(self):
        return createToken()

    @memoize
    def can_edit(self):
        return bool(getSecurityManager().checkPermission(
            'Portlets: Manage own portlets',
            self.context
        ))

    @memoize
    def empty(self):
        dashboards = [
            getUtility(IPortletManager, name=name) for name in
            [
                'plone.dashboard1',
                'plone.dashboard2',
                'plone.dashboard3',
                'plone.dashboard4'
            ]
        ]

        portal_membership = getToolByName(self.context, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        userid = member.getId()

        num_portlets = 0
        for dashboard in dashboards:
            num_portlets += len(dashboard.get(
                USER_CATEGORY, {}).get(userid, {}))
            for groupid in member.getGroups():
                num_portlets += len(dashboard.get(
                    GROUP_CATEGORY, {}).get(groupid, {}))
        return num_portlets == 0
