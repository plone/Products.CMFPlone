## Script (Python) "content_status_modify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=workflow_action, comment='', effective_date=None, expiration_date=None
##title=less lazy contenet status modify script
##

if effective_date or expiration_date:
    context.metadata_edit(effective_date=effective_date,
                          expiration_date=expiration_date)

context.portal_workflow.doActionFor(
    context,
    workflow_action,
    comment=comment)

typeObj=context.portal_types.getTypeInfo(context)
view=typeObj.getActionById('view')

redirect_url = '%s/%s?%s' % ( context.absolute_url()
                            , view
                            , 'portal_status_message=Status+changed.')
			    
context.REQUEST[ 'RESPONSE' ].redirect( redirect_url )

