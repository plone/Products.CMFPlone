## Script (Python) "folder_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Publish objects from a folder
##
REQUEST=context.REQUEST
workflow = context.portal_workflow
try:
    if REQUEST.has_key('ids'):
      for id in REQUEST['ids']:
        o = getattr(context, id)
        workflow.doActionFor(o, 'publish', comment='Published from folder_contents')
    return REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_contents?portal_status_message=Content+published.')
except Exception, e:
    REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_contents?portal_status_message='+str(e))

