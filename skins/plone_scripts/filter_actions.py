## Script (Python) "filter_actions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=self=None, filter_map={}, html=0
##title=
##
REQUEST=context.REQUEST

actions = None
act_text = '<a href="%s" class="passive">%s</a> <span class="netscape4">&middot;</span>'

context.plone_debug('inside filter_action ' + str(REQUEST.has_key('filtered_actions')))
if self:
    actions = REQUEST.get('filtered_actions', context.portal_actions.listFilteredActionsFor(self))
else:
    actions = REQUEST.get('filtered_actions', context.portal_actions.listFilteredActionsFor(context))

filtered = {}

for category in filter_map.keys():
    for action in actions[category]:
        if action['name'] in filter_map[category]:
            filtered[action['name']]=action['url']
        
return filtered
