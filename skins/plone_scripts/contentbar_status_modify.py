## Script (Python) "contentbar_status_modify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=workflow_action, comment='', effective_date=None, expiration_date=None
##title=Copy object from a folder to the clipboard
##
portal_workflow=context.portal_workflow
current_state=portal_workflow.getInfoFor(context, 'review_state')

if workflow_action!=current_state and not effective_date:
    effective_date=DateTime()

context.plone_utils.contentEdit( context
                               , effective_date=effective_date
                               , expiration_date=expiration_date )

if workflow_action!=current_state:
    context.portal_workflow.doActionFor( context
                                       , workflow_action
                                       , comment=comment )
msg='portal_status_message=Your+contents+status+has+been+modified.'

context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , context.getTypeInfo().getActionById( 'view' )
                                                , msg
                                                ) )

