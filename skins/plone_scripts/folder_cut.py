## Script (Python) "folder_cut"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Cut objects from a folder and copy to the clipboard
##
REQUEST=context.REQUEST
if REQUEST.has_key('ids'):
  context.manage_cutObjects(REQUEST['ids'], REQUEST)
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_contents?portal_status_message=Item(s)+Cut.')
else:
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_contents?portal_status_message=Please+select+one+or+more+items+to+cut+first.')
