## Controller Python Script "enableSyndication"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Enable Syndication for a resource
##parameters=
state = context.portal_form_controller.getState(script, is_validator=0)

if context.portal_syndication.isSiteSyndicationAllowed():
    context.portal_syndication.enableSyndication(context)
    portal_status_message="Syndication enabled"
else:
    portal_status_message="Syndication not allowed"

return state.set(portal_status_message=portal_status_message)


