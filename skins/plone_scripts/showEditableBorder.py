##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=template_id=None
##title=returns whether or not current template displays *editable* border
##
REQUEST=context.REQUEST
actions=[]

if REQUEST.get('filtered_actions', ''): #short circuit listFilteredActionsFor
    actions=REQUEST['filtered_actions']
else:
    actions=container.portal_actions.listFilteredActionsFor(context)

if ( getattr(context, 'isPortalContent', 0) and \
     'edit' in [ o.get('id', '') for o in actions.get('object', ()) ] ) or \
     'edit' in [ f.get('id', '') for f in actions.get('folder', ()) ] :
    return 1

return 0
