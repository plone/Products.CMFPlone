## Script (Python) "getOrderedUserActions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=keyed_actions=None, ordering=None
##title=Depending on the context return the actions for a personalbar
##

context.plone_log("The getOrderedUserActions script is deprecated and will be "
                  "removed in Plone 4.0.")

if keyed_actions is None:
    keyed_actions=context.keyFilteredActions()

if ordering is None:
    preordering=['mystuff', 'preferences', 'undo']
    postordering=['configPortal', 'logout']
else:
    preordering=ordering['pre']
    postordering=ordering['post']

totalordering=preordering+postordering

ordered_actions=[]
user_actions=keyed_actions['user']

for id in preordering:
    if user_actions.get(id, None) is not None:
        ordered_actions.append( user_actions[id].copy() )

ordered_actions+=[ action.copy() for action in user_actions.values()
                   if action['id'] not in totalordering ]

for id in postordering:
    if user_actions.get(id, None) is not None:
        ordered_actions.append( user_actions[id].copy() )

return ordered_actions
