## Script (Python) "folder_publish"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ids, workflow_action, comment='No comment', expiration_date=None, effective_date=None, include_subfolders=0
##title=Publish objects from a folder
##
REQUEST=context.REQUEST
workflow = context.portal_workflow

failed = {}
success = {}

for id in ids:
    o = getattr(context, id)
    try:
        if o.isPrincipiaFolderish and REQUEST.get('include_subfolders', ''):
            o.folder_publish(o.objectIds(), workflow_action, comment)       
        else:
            workflow.doActionFor(o, workflow_action, comment=comment)
            success[id]=comment
    except Exception, e:
        failed[id]=e

REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                        , 'folder_contents'
					, 'portal_status_message=Content(s)+have+been+changed.') )
				
#view = getattr(context, 'folder_contents')
#return view(REQUEST, failed, success)

