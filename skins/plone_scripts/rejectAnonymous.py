## Script (Python) "rejectAnonymous"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

if context.portal_membership.isAnonymousUser():
    portal_url=context.portal_url()
    RESPONSE=context.REQUEST.RESPONSE
    url = '%s/%s?%s'
    msg = 'portal_status_message=You+must+sign+in+first.'
    return RESPONSE.redirect( url % ( portal_url
                                    , 'login_form'
                                    , msg ) )
return 1

