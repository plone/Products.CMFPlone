## Script (Python) "folder_publish"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=workflow_action=None, ids=[], comment='No comment', expiration_date=None, effective_date=None, include_subfolders=0
##title=Publish objects from a folder
##
from Products.CMFPlone import transaction_note
plone_utils=context.plone_utils
REQUEST=context.REQUEST
workflow = context.portal_workflow
failed = {}
success = {}

if workflow_action is None:
    return context.portal_navigation.getNext( context
                , script.getId()
                , 'failure'
                , portal_status_message='You must select a publishing action.')
if not ids:
    return context.portal_navigation.getNext( context
                , script.getId()
                , 'failure'
                , portal_status_message='You must select content to change.')

for id in ids:
    o = getattr(context, id)
    try:
        if o.isPrincipiaFolderish and include_subfolders:
            workflow.doActionFor(o, workflow_action, comment=comment)
            o.folder_publish(workflow_action, o.objectIds(), comment=comment, \
                 include_subfolders=include_subfolders, effective_date=effective_date, \
                 expiration_date=expiration_date)       
        else:
            workflow.doActionFor(o, workflow_action, comment=comment)
            success[id]=comment
        plone_utils.contentEdit(o, effective_date=effective_date, expiration_date=expiration_date)
    except Exception, e:
        failed[id]=e

transaction_note( str(ids) + ' transitioned ' + workflow_action )

return context.portal_navigation.getNext( context
            , script.getId()
            , 'success'
            , portal_status_message='Content has been changed.')
