## Script (Python) "showEditableBorder"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=template_id
##title=returns whether or not current template displays *editable* border
##
actions=container.portal_actions.listFilteredActionsFor(context)
wf_actions=actions.get('workflow', ())
obj_actions=actions.get('object', ())

# no special cases; just check if we have tabs to show
# listFilteredActionsFor does all the rest for us

return wf_actions or len(obj_actions) > 1
