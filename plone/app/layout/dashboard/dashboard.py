from zope.component import getUtility
from zope.i18n import translate

from Products.Five.browser import BrowserView

from plone.portlets.interfaces import IPortletManager
from plone.portlets.constants import USER_CATEGORY

from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName

class DashboardView(BrowserView):
    """Power the dasbhard
    """

    def actions(self):
        portal_actions = getToolByName(self.context, 'portal_actions')
        categories = 'controlpanel/controlpanel_user'
        actions = portal_actions.listActionInfos(categories=categories)
        def _title(v):
            return translate(v.get('title'),
                             domain='plone',
                             context=self.request)
        actions.sort(key=_title)
        return actions

    @memoize
    def empty(self):
        dashboards = [getUtility(IPortletManager, name=name) for name in
                        ['plone.dashboard1', 'plone.dashboard2', 'plone.dashboard3', 'plone.dashboard4']]
                        
        portal_membership = getToolByName(self.context, 'portal_membership')
        userid = portal_membership.getAuthenticatedMember().getId()
                        
        num_portlets = 0
        for dashboard in dashboards:
            num_portlets += len(dashboard.get(USER_CATEGORY, {}).get(userid, {}))
        return num_portlets == 0
