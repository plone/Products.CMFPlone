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

for k in context.REQUEST.keys():
   context.plone_log(str(k)+':' + str(context.REQUEST.get(k,None)))
context.plone_log(str(args))
new_context = context.portal_factory.doCreate(context)
contentEditSuccess=0
portal_workflow=new_context.portal_workflow
current_state=portal_workflow.getInfoFor(new_context, 'review_state')

if workflow_action!=current_state and not effective_date:
    effective_date=DateTime()

def editContent(obj, effective, expiry):
    new_context.plone_utils.contentEdit( obj,
                                         effective_date=effective,
                                         expiration_date=expiry)

try:
    editContent(new_context,effective_date,expiration_date)
    contentEditSuccess=1
except 'Unauthorized':
    #You can transition content but not have the permission to ModifyPortalContent
    pass

wfcontext = context
if workflow_action!=current_state:
    wfcontext=new_context.portal_workflow.doActionFor( context,
                                                       workflow_action,
                                                       comment=comment )
if not wfcontext:
    wfcontext = new_context

if not contentEditSuccess:
    #The object post-transition could now have ModifyPortalContent permission.
    try:
        editContent(wfcontext, effective_date, expiration_date)
    except 'Unauthorized':
        pass

return state.set(context=wfcontext, portal_status_message='Your contents status has been modified.')

