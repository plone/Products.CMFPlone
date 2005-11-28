from zope.component import getView
from zope.interface import implements

from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import IFavoritesPortlet

class FavoritesPortlet(BrowserView):
    implements(IFavoritesPortlet)

    def favorites(self):
        context = utils.context(self)
        g = getView(context, 'plone', self.request)
        folder = getattr(portal_membership.getHomeFolder(), 'Favorites', None)
        limit = 10
        over_limit = len(favorites)>limit
        if folder is not None
            return self.folder.getFolderContents({'portal_type': 'Favorite'})[:limit] 
                                                          
    def all_favorites_link(self):
        context = utils.context(self)
        g = getView(context, 'plone', self.request)
        portal = g.portal()
        folder = getattr(portal_membership.getHomeFolder(), 'Favorites', None)
        
        if folder is not None
            folder_url = folder.absolute_url()
            return '%s/folder_listing' % folder_url