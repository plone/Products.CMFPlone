## Script (Python) "require_login"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Login
##
membership_tool=context.portal_membership
isAnonymous = membership_tool.isAnonymousUser()
login = 'login_form'
insufficient_privileges = 'insufficient_privileges'
request = context.REQUEST

if isAnonymous:
    query = request.get('QUERY_STRING','')
    if query:
        query = '?'+query
    return request.RESPONSE.redirect(context.portal_url()+'/'+login+query)
else:
    return request.RESPONSE.redirect(context.portal_url()+'/'+insufficient_privileges)
