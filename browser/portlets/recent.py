from Products.CMFPlone.browser.interfaces import IRecentPortlet

from zope.interface import implements
from zope.component import getView
from Products.CMFPlone import utils


class RecentPortlet(utils.BrowserView):
    implements(IRecentPortlet)

    def results(self):
        """ """
        context = utils.context(self)
        g = getView(context, 'globals_view', self.request)
        portal_catalog = g.portal().portal_catalog
        typesToShow = g.putils().getUserFriendlyTypes()
        return self.request.get(
            'items',
            portal_catalog.searchResults(sort_on='modified',
                                         portal_type=typesToShow,
                                         sort_order='reverse')[:5])
