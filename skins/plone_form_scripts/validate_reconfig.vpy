## Controller Python Script "validate_reconfig"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=validates the portal config

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state.set(portal_status_message='You have been registered.')
