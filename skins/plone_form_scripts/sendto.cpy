## Controller Python Script "sendto"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Send an URL to a friend
##
REQUEST=context.REQUEST

plone_utils=context.plone_utils
site_properties=context.portal_properties.site_properties

if not site_properties.allow_sendto:
    return state.set(status='failure', portal_status_message='You are not allowed to send this link.')

variables = { 'send_from_address' : REQUEST.send_from_address
            , 'send_to_address'   : REQUEST.send_to_address
            , 'url'               : context.absolute_url()
            , 'title'             : context.Title()
            , 'description'       : context.description
            , 'comment'           : REQUEST.get('comment',None)
            }
try:
    plone_utils.sendto( variables )
except:
    exception = context.plone_utils.exceptionString()
    return state.set(status='failure', portal_status_message=exception)

return state.set(portal_status_message='Mail sent.')
