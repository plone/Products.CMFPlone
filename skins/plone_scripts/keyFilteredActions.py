## Script (Python) "keyFilteredActions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=actions=None
##title=
##

if actions is None:
    actions=context.portal_actions.listFilteredActionsFor()

keyed_actions={}

for category in actions.keys():
    keyed_actions[category]={}
    for action in actions[category]:
        keyed_actions[category][action['id']]=action.copy()

return keyed_actions


