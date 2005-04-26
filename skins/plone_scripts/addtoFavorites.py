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
    msg = "Can't access home folder. Favorite is not added"
    return RESPONSE.redirect('%s?portal_status_message=%s' % (view_url, msg))

if not hasattr(homeFolder, 'Favorites'):
    homeFolder.invokeFactory('Folder', id='Favorites')

targetFolder = homeFolder.Favorites
new_id='fav_' + str(int( context.ZopeTime()))
myPath=context.portal_url.getRelativeUrl(context)
targetFolder.invokeFactory('Favorite', id=new_id, title=context.TitleOrId(), remote_url=myPath)

msg = context.translate("${title} has been added to your Favorites.",
                        {'title': context.title_or_id()})

return RESPONSE.redirect('%s?portal_status_message=%s' % (view_url, msg))
