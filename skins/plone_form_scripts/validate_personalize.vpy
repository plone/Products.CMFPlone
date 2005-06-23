## Controller Python Script "validate_personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=email=''
##title=validates user preferences

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.')
    return state.set(status='failure')
else:
    context.plone_utils.addPortalMessage('You have been registered.')
    return state
