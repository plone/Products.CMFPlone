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

# lets attempt to short circuit listFilteredActionsFor, which is expensive!
if REQUEST.get('filtered_actions', ''): 
    actions=REQUEST['filtered_actions']
else:
    actions=container.portal_actions.listFilteredActionsFor(context)

obj_actions=actions.get('object', ())
folder_actions=actions.get('folder', ())

objectActionIds = [ o.get('id', '') for o in obj_actions ]
if getattr(context, 'isPortalContent', 0) and 'edit' in objectActionIds: 
    return 1

folderActionsIds = [ f.get('id', '') for f in folder_actions]
if 'edit' in folderActionsIds:
    return 1

return 0
