## Script (Python) "contentbar_status_modify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=workflow_action, comment='', effective_date=None, expiration_date=None
##title=Copy object from a folder to the clipboard
##
RESPONSE=context.REQUEST.RESPONSE
msg='portal_status_message=Your+contents+status+has+been+modified.'

context.content_status_modify(workflow_action,
                              comment,
                              effective_date,
                              expiration_date)

RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url(),
                                  context.getTypeInfo().getActionById( 'view' ),
                                  msg ) )
