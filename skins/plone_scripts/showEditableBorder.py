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
    if action.get('id', '')!='view':
        return 1

if template_id is None and hasattr(REQUEST['PUBLISHED'], 'getId'):
    template_id=REQUEST['PUBLISHED'].getId()

if actions.get('workflow', ()):
    return 1

idActions = {}
for obj in actions.get('object', ()) + actions.get('folder', ()):
    idActions[obj.get('id', '')] = 1

if idActions.has_key('edit') :
    if (idActions.has_key(template_id) or \
        template_id in ['synPropertiesForm', 'folder_contents', 'folder_listing']) :
        return 1

# Check to see if the user is able to add content or change workflow state
if context.getAllowedTypes():
    return 1
if context.portal_workflow.getTransitionsFor(context, context):
    return 1

return 0
