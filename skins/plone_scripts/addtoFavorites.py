## Script (Python) "addtoFavorites"
##title=Add item to favourites (Plone Version)
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone import PloneMessageFactory as _
from Products.PythonScripts.standard import url_quote_plus

RESPONSE = context.REQUEST.RESPONSE
homeFolder=context.portal_membership.getHomeFolder()
view_url = '%s/%s' % (context.absolute_url(),
                      context.getTypeInfo().getActionById('view')
                     )

if not homeFolder:
    msg = _(u'Can\'t access home folder. Favorite is not added.')
    return RESPONSE.redirect('%s?portal_status_message=%s' % (view_url, url_quote_plus(msg)))

if not base_hasattr(homeFolder, 'Favorites'):
    homeFolder.invokeFactory('Folder', id='Favorites', title='Favorites')
    addable_types = ['Favorite']
    favs = homeFolder.Favorites
    if base_hasattr(favs, 'setConstrainTypesMode'):
        favs.setConstrainTypesMode(1)
        favs.setImmediatelyAddableTypes(addable_types)
        favs.setLocallyAllowedTypes(addable_types)

targetFolder = homeFolder.Favorites
new_id='fav_' + str(int( context.ZopeTime()))
myPath=context.portal_url.getRelativeUrl(context)
targetFolder.invokeFactory('Favorite', id=new_id, title=context.TitleOrId(), remote_url=myPath)

msg = _(u'${title} has been added to your Favorites.')
msg.mapping[u'title'] = context.title_or_id()

return RESPONSE.redirect('%s?portal_status_message=%s' % (view_url, url_quote_plus(msg)))
