## Script (Python) "showEditableBorder"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=template_id=None, actions=None
##title=returns whether or not current template displays *editable* border
##

#XXX This is an ugly hack.  So it might as well
#    be explained.  Traditionally in CMF actions
#    are lumped in by categories.  workflow/object/folder and more.
#    well.  to show a green border means that the user can
#    interact with the content.  We have to sort of 'action scrap'
#    since 'view' is a action by default anonymous can see we need
#    to make sure 'view' isnt the only action they can do on the object
#    Also we check to see if PUBLISHED method (we have access to because
#    it did publish) is in the actions somewhere.  
#    
#    Alot of this could be refactored if Actions could do filter for you
#    but I cant suggest right now.  Something like 'I want to query'
#    only actions that are declared for a type in the types tool. It would
#    be convient to be able to get actions from the ActionProviders as well
#    as the portal_actions (aggregate of all ActionProviders)
#

REQUEST=context.REQUEST

if actions is None:
    raise 'You must pass in the filtered actions'
    
if REQUEST.has_key('disable_border'): #short circuit
    return 0 
if REQUEST.has_key('enable_border'): #short circuit
    return 1
    
for action in actions.get('object', []):
    if action.get('id', '')!='view' and action.get('id', '')!='folderContents': 
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

