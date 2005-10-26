## Script (Python) "redirectToReferrer"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=message
##title=Redirect to Referrer with message
##
from Products.PythonScripts.standard import url_quote_plus
request=context.REQUEST
referer=request.get('HTTP_REFERER', '')
query_pos=referer.find('?')
if query_pos != -1:
    target_url=referer[:referer.find('?')]
else:
    target_url=referer
return request.RESPONSE.redirect('%s?portal_status_message=%s' % ( target_url,
                                   url_quote_plus(message)))
