## Script (Python) "content_status_modify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=workflow_action, comment='', effective_date=None, expiration_date=None
##title=handles the workflow transitions of objects
##

if effective_date or expiration_date:
    context.plone_utils.contentEdit( context
                                   , effective_date=effective_date
                                   , expiration_date=expiration_date )
                                   
context.portal_workflow.doActionFor( context
                                   , workflow_action
                                   , comment=comment )

return ('success', context)
