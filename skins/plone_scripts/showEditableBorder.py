##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=template_id=None
##title=returns whether or not current template displays *editable* border
##
if template_id is None:
    REQUEST=context.REQUEST
    template_id=REQUEST['PUBLISHED'].getId()

show_border=0
actions=container.portal_actions.listFilteredActionsFor(context)
wf_actions=actions.get('workflow', ())
obj_actions=actions.get('object', ())
folder_actions=actions.get('folder', ())

def idInActions(seq, action_id):
    for a in seq:
        if a.get('id','name').lower()==action_id:
            return 1
    return None

# no special cases; just check if we have tabs to show
# listFilteredActionsFor does all the rest for us
# XXX - runyaga; I wish it could be this simple ;(
# show_border = wf_actions or len(obj_actions) > 1 #in CMF1.2 'log in' is a wf_action!

if context.isPrincipiaFolderish:
    if idInActions(folder_actions, 'edit'): 
        return 1
    if (template_id=='folder_contents' or template_id=='folder_listing') \
        and container.portal_membership.checkPermission( 'List folder contents', context):
        show_border = 1
else:
    if idInActions(obj_actions, 'edit'): 
        return 1

return show_border
