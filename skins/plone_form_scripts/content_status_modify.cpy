## Controller Python Script "content_status_modify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=workflow_action, comment='', effective_date=None, expiration_date=None
##title=handles the workflow transitions of objects
##
newcontext=context
contentEditSuccess=0
portal_workflow=context.portal_workflow
current_state=portal_workflow.getInfoFor(context, 'review_state')
state = context.portal_form_controller.getState(script, is_validator=0)

if workflow_action!=current_state and not effective_date:
    effective_date=DateTime()

def editContent(obj, effective, expiry):
    context.plone_utils.contentEdit( obj,
                                     effective_date=effective,
                                     expiration_date=expiry)

try:
    editContent(context,effective_date,expiration_date)
    contentEditSuccess=1
except 'Unauthorized':
    #You can transition content but not have the permission to ModifyPortalContent
    pass

if workflow_action!=current_state:
    newcontext=context.portal_workflow.doActionFor( context,
                                                    workflow_action,
                                                    comment=comment )
if not newcontext:
    newcontext = context

if not contentEditSuccess:
    #The object post-transition could now have ModifyPortalContent permission.
    try:
        editContent(newcontext, effective_date, expiration_date)
    except 'Unauthorized':
        pass

return state.set(context=newcontext, portal_status_message='Your contents status has been modified.')

