## Script (Python) "folder_paste"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Paste objects to a folder from the clipboard
##
REQUEST=context.REQUEST
if context.cb_dataValid:
  context.manage_pasteObjects(REQUEST['__cp'])
#  context.afterPasteAction(context, REQUEST['__cp']) #our lil fix to guarantee unique ids
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_contents?portal_status_message=Item(s)+Pasted.')
else:
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_contents?portal_status_message=Copy+or+cut+one+or+more+items+to+paste+first.')
