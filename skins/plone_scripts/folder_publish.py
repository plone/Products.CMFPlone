## Script (Python) "folder_publish"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=workflow_action, ids=[], comment='No comment', expiration_date=None, effective_date=None, include_subfolders=0
##title=Publish objects from a folder
##
from Products.CMFPlone import transaction_note
REQUEST=context.REQUEST
workflow = context.portal_workflow
failed = {}
success = {}

if not ids:
    return REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                    , 'folder_contents'
                                    , 'portal_status_message=You+must+select+content+to+change.') )

for id in ids:
    o = getattr(context, id)
    try:
        if o.isPrincipiaFolderish and include_subfolders:
            workflow.doActionFor(o, workflow_action, comment=comment)
            o.folder_publish(workflow_action, o.objectIds(), comment=comment, include_subfolders=include_subfolders)       
        else:
            workflow.doActionFor(o, workflow_action, comment=comment)
            success[id]=comment
    except Exception, e:
        failed[id]=e

transaction_note( str(ids) + ' transitioned ' + workflow_action )

REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                        , 'folder_contents'
					, 'portal_status_message=Content(s)+have+been+changed.') )
				
