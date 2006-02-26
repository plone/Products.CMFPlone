from Products.CMFPlone.browser.interfaces import IRecentPortlet
from Products.CMFCore.utils import getToolByName

from zope.interface import implements
from Products.CMFPlone import utils


class RecentPortlet(utils.BrowserView):
    implements(IRecentPortlet)

    def results(self):
        """ """
        context = utils.context(self)
        putils = getToolByName(context, 'plone_utils')
        portal_catalog = getToolByName(context, 'portal_catalog')
        typesToShow = putils.getUserFriendlyTypes()
        return self.request.get(
            'items',
            portal_catalog.searchResults(sort_on='modified',
                                         portal_type=typesToShow,
                                         sort_order='reverse')[:5])
