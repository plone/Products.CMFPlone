## Script (Python) "rate_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=rating
##title=
##
REQUEST = context.REQUEST
ratings_tool = context.portal_ratings
ratings = ratings_tool.getRatingFor(context)

try:
    ratings.addRating(rating)
    status_msg = 'Rating+has+been+calculated.'
except Exception:
    status_msg = 'Anonymous+not+allowed+to+rate+content.'

return REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                               , context.getTypeInfo().getActionById('view')
                                               , 'portal_status_message=' + status_msg ) )

