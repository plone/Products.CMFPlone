##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=template_id=None, actions=None
##title=returns whether or not current template displays *editable* border
##
""" assumes the object has a edit property """
if actions is None:
    raise 'You must pass in the filtered actions'
    
REQUEST=context.REQUEST
for action in actions.get('object', []):
    if action.get('id', '')!='view':
        return 1

if template_id is None and hasattr(REQUEST['PUBLISHED'], 'getId'):
    template_id=REQUEST['PUBLISHED'].getId()

if ( 'edit' in [ o.get('id', '') for o in actions.get('object', ()) ] or \
     'edit' in [ f.get('id', '') for f in actions.get('folder', ()) ] or \
     actions.get('workflow', ()) ) :
   
    if ( template_id in [ o.get('action', '') for o in actions.get('object', ()) ] or \
         template_id in [ f.get('action', '') for f in actions.get('folder', ()) ] or \
         template_id in ['synPropertiesForm', 'folder_contents', 'folder_listing'] or \
	 actions.get('workflow', ()) ) :
        return 1

return 0

