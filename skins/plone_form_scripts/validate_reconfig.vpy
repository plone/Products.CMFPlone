## Controller Python Script "validate_reconfig"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=validates the portal config

# nothing to check?
#if state.getErrors():
#    context.plone_utils.addPortalMessage('Please correct the indicated errors.')
#    return state.set(status='failure')
return state
