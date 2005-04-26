## Controller Python Script "setConstrainTypes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##title=Set the options for constraining addable types on a per-folder basis

constrainTypesMode = context.REQUEST.get('constrainTypesMode', [])
locallyAllowedTypes = context.REQUEST.get('locallyAllowedTypes', [])
immediatelyAddableTypes = context.REQUEST.get('immediatelyAddableTypes', [])

context.setConstrainTypesMode(constrainTypesMode)
context.setLocallyAllowedTypes(locallyAllowedTypes)
context.setImmediatelyAddableTypes(immediatelyAddableTypes)

portal_status_message = "Changes made"

return state.set(portal_status_message=portal_status_message)


