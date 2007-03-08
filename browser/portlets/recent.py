import zope.deprecation
from zope.interface import implements
from zope.component import getUtility

from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import IRecentPortlet
from Products.CMFCore.interfaces import ICatalogTool
from Products.CMFPlone.interfaces import IPloneTool


class RecentPortlet(utils.BrowserView):
    implements(IRecentPortlet)

    def results(self):
        """ """
        context = utils.context(self)
        putils = getUtility(IPloneTool)
        portal_catalog = getUtility(ICatalogTool)
        typesToShow = putils.getUserFriendlyTypes()
        return self.request.get(
            'items',
            portal_catalog.searchResults(sort_on='modified',
                                         portal_type=typesToShow,
                                         sort_order='reverse',
                                         sort_limit=5)[:5])

zope.deprecation.deprecated(
  ('RecentPortlet', ),
   "Plone's portlets are based on plone.app.portlets now. The old portlets "
   "will be removed in Plone 3.5."
  )
