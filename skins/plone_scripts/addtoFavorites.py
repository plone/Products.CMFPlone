## Script (Python) "addtoFavorites"
##title=Add item to favourites (Plone Version)
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
homeFolder=context.portal_membership.getHomeFolder()
if not hasattr(homeFolder, 'Favorites'):
  homeFolder.manage_addPortalFolder(id='Favorites', title='Favorites')

targetFolder = getattr( homeFolder, 'Favorites' )
new_id='fav_' + str(int( context.ZopeTime()))
myPath=context.portal_url.getRelativeUrl(context)
targetFolder.invokeFactory( 'Favorite', id=new_id, title=context.TitleOrId(), remote_url=myPath)

msg = 'portal_status_message=\''+context.title_or_id()+'\'+has+been+added+to+your+Favorites'
return context.REQUEST.RESPONSE.redirect('%s/%s?%s' % ( context.absolute_url()
                                                      , context.getTypeInfo().getActionById('view')
                                                      , msg ))
