## Script (Python) "addtoFavorites"
##title=Add item to favourites
##bind namespace=_
##parameters=plone version
homeFolder=context.portal_membership.getHomeFolder()
if not hasattr(homeFolder, 'Favorites'):
  homeFolder.manage_addPortalFolder(id='Favorites', title='Favorites')

targetFolder = getattr( homeFolder, 'Favorites' )
new_id='fav_' + str(int( context.ZopeTime()))
myPath=context.portal_url.getRelativeUrl(context)
targetFolder.invokeFactory( 'Favorite', id=new_id, title=context.TitleOrId(), remote_url=myPath)

msg = 'portal_status_message='+context.getId()+'+added+to+favorites'
return context.REQUEST.RESPONSE.redirect('%s/%s?%s' % ( context.absolute_url()
                                                      , context.getTypeInfo().getActionById('view')
                                                      , msg ))
