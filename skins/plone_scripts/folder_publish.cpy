## Controller Python Script "folder_publish"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=workflow_action=None, ids=[], comment='No comment', expiration_date=None, effective_date=None, include_subfolders=0
##title=Publish objects from a folder
##

from Products.CMFPlone import transaction_note
plone_utils=context.plone_utils
REQUEST=context.REQUEST
workflow = context.portal_workflow
content_status_modify=context.content_status_modify
failed = {}
success = {}

if workflow_action is None:
    return state.set(status='failure', portal_status_message='You must select a publishing action.')
if not ids:
    return state.set(status='failure', portal_status_message='You must select content to change.')

for id in ids:
    o = getattr(context, id)
    try:
        if o.isPrincipiaFolderish and include_subfolders:
            workflow.doActionFor(o, workflow_action, comment=comment)
            o.folder_publish( workflow_action, 
                              o.objectIds(), 
                              comment=comment, 
                              include_subfolders=include_subfolders, 
                              effective_date=effective_date,
                              expiration_date=expiration_date )
        else:
            o.content_status_modify( workflow_action,
                                     comment,
                                     effective_date=effective_date,
                                     expiration_date=expiration_date )
            success[id]=comment
    except Exception, e:
        failed[id]=e

transaction_note( str(ids) + ' transitioned ' + workflow_action )

# It is necessary to set the context to override context from content_status_modify
return state.set(context=context, portal_status_message='Content has been changed.')
