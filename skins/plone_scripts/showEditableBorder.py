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

show_border=0
isPortalContent = getattr(context, 'isPortalContent', 0)
checkPermission = container.portal_membership.checkPermission

if folder_actions and \
   template_id in ['folder_listing', 'folder_contents'] and \
   checkPermission( 'List folder contents', context):
    show_border = 1
elif isPortalContent and idInActions(obj_actions, 'edit'): 
    show_border = 1 

#elif idInActions(folder_actions, 'edit'): #if you can edit the folder
#    show_border = 1

return show_border
