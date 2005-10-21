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

    from Products.CMFPlone import PloneMessageFactory as _
    from Products.PythonScripts.standard import url_quote_plus

    portal_url=context.portal_url()
    RESPONSE=context.REQUEST.RESPONSE
    url = '%s/login_form?portal_status_message=%s'
    msg = _(u'You must sign in first.')
    return RESPONSE.redirect( url % ( portal_url
                                    , url_quote_plus(msg) ) )
return 1
