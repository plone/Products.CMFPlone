## Script (Python) "addtoFavorites"
##title=Add item to favourites (Plone Version)
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
RESPONSE = context.REQUEST.RESPONSE
homeFolder=context.portal_membership.getHomeFolder()
view_url = '%s/%s' % (context.absolute_url(),
                      context.getTypeInfo().getActionById('view')
                     )

if not homeFolder:
    msg = 'portal_status_message=Can\'t access home folder. Favorite is not added'
    return RESPONSE.redirect('%s?%s' % (view_url, msg))

if not hasattr(homeFolder, 'Favorites'):
    homeFolder.invokeFactory('ATFolder', id='Favorites')

targetFolder = homeFolder.Favorites
new_id='fav_' + str(int( context.ZopeTime()))
myPath=context.portal_url.getRelativeUrl(context)
targetFolder.invokeFactory( 'ATFavorite', id=new_id, title=context.TitleOrId(), remote_url=myPath)

msg = 'portal_status_message=\'%s\' has been added to your Favorites' % context.title_or_id()
return RESPONSE.redirect('%s?%s' % (view_url, msg))
