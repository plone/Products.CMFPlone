from zope.interface import implements
from zope.component import adapts, queryUtility

from zope.container.interfaces import INameChooser

from Products.PluggableAuthService.interfaces.authservice import IPropertiedUser

from plone.portlets.interfaces import IPortletManager
from plone.portlets.constants import USER_CATEGORY

from plone.app.portlets.interfaces import IDefaultDashboard
from plone.app.portlets import portlets

from plone.app.portlets.storage import UserPortletAssignmentMapping

def new_user(principal, event):
    """Initialise the dashboard for a new user
    """
    defaults = IDefaultDashboard(principal, None)
    if defaults is None:
        return

    userid = principal.getId()
    portlets = defaults()

    for name in ('plone.dashboard1', 'plone.dashboard2', 'plone.dashboard3', 'plone.dashboard4'):
        assignments = portlets.get(name)
        if assignments:
            column = queryUtility(IPortletManager, name=name)
            if column is not None:
                category = column.get(USER_CATEGORY, None)
                if category is not None:
                    manager = category.get(userid, None)
                    if manager is None:
                        manager = category[userid] = UserPortletAssignmentMapping(manager=name,
                                                                                  category=USER_CATEGORY,
                                                                                  name=userid)
                    chooser = INameChooser(manager)
                    for assignment in assignments:
                        manager[chooser.chooseName(None, assignment)] = assignment

class DefaultDashboard(object):
    """The default default dashboard.
    """

    implements(IDefaultDashboard)
    adapts(IPropertiedUser)

    def __init__(self, principal):
        self.principal = principal

    def __call__(self):
        return {
            'plone.dashboard1' : (portlets.news.Assignment(), portlets.events.Assignment(),),
            'plone.dashboard2' : (portlets.recent.Assignment(),),
            'plone.dashboard3' : (),
            'plone.dashboard4' : (portlets.review.Assignment(),),
        }