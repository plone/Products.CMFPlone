## Script (Python) "keyFilteredActions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=actions=None
##title=
##

#If action does not have an ID it will not
#show up in the keyedActions.

if actions is None:
    actions=context.portal_actions.listFilteredActionsFor()

keyed_actions={}

for category in actions.keys():
    keyed_actions[category]={}
    for action in actions[category]:
        id=action.get('id',None)
        if id is not None:
            keyed_actions[category][id]=action.copy()

return keyed_actions


