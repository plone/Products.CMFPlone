## Script (Python) "redirectToReferrer"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=message
##title=Redirect to Referrer with message
##

request=context.REQUEST
referer=request.get('HTTP_REFERER', '')
query_pos=referer.find('?')
if query_pos != -1:
    target_url=referer[:referer.find('?')]
else:
    target_url=referer
return request.RESPONSE.redirect(target_url)
