## Controller Python Script "content_status_modify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=workflow_action=None, comment='', effective_date=None, expiration_date=None, *args
##title=handles the workflow transitions of objects
##

contentEditSuccess=0
plone_log=context.plone_log
new_context = context.portal_factory.doCreate(context)
portal_workflow=new_context.portal_workflow
current_state=portal_workflow.getInfoFor(new_context, 'review_state')

if workflow_action!=current_state and not effective_date:
    effective_date=DateTime()

#plone_log('effective date ' + str(effective_date))

def editContent(obj, effective, expiry):
    new_context.plone_utils.contentEdit( obj,
                                         effective_date=effective,
                                         expiration_date=expiry)

#You can transition content but not have the permission to ModifyPortalContent
try:
    editContent(new_context,effective_date,expiration_date)
    contentEditSuccess=1
except 'Unauthorized':
    pass

wfcontext = context
if workflow_action!=current_state:
    wfcontext=new_context.portal_workflow.doActionFor( context,
                                                       workflow_action,
                                                       comment=comment )
if not wfcontext:
    wfcontext = new_context

#The object post-transition could now have ModifyPortalContent permission.
if not contentEditSuccess:
    try:
        editContent(wfcontext, effective_date, expiration_date)
    except 'Unauthorized':
        pass

return state.set(context=wfcontext,
                 portal_status_message='Your contents status has been modified.')

