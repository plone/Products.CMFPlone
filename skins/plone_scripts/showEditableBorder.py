## Script (Python) "showEditableBorder"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=template_id
##title=returns whether or not current template displays *editable* border
##
actions=context.portal_actions.listFilteredActionsFor(context)
anonymous=membership.isAnonymousUser()
wf_actions=actions.get('workflow', ())
obj_actions=actions.get('object', ())

# no special cases; just check if we have tabs to show
# listFilteredActionsFor does all the rest for us

return wf_actions or len(wf_actions) > 1
