## Script (Python) "folder_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Delete objects from a folder
##
REQUEST=context.REQUEST
if REQUEST.has_key('ids'):
  context.manage_delObjects(REQUEST['ids'], REQUEST)
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_contents?portal_status_message=Deleted.')
else:
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_contents?portal_status_message=Please+select+one+or+more+items+first.')
