from Acquisition import aq_inner
import zope.deprecation
from zope.interface import implements

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.interfaces import IRecentPortlet


class RecentPortlet(BrowserView):
    implements(IRecentPortlet)

    def results(self):
        """ """
        context = aq_inner(self.context)
        putils = getToolByName(context, 'plone_utils')
        portal_catalog = getToolByName(context, 'portal_catalog')
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
   "will be removed in Plone 4.0."
  )
