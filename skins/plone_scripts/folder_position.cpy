## Controller Python Script "folder_position"
##title=Move objects in a ordered folder
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=position, id, template_id='folder_contents'
##
from Products.PythonScripts.standard import url_quote

if position.lower()=='up':
    context.moveObjectsUp(id)

if position.lower()=='down':
    context.moveObjectsDown(id)

if position.lower()=='top':
    context.moveObjectsToTop(id)

if position.lower()=='bottom':
    context.moveObjectsToBottom(id)

# order folder by field
# id in this case is the field
if position.lower()=='ordered':
    context.orderObjects(id)

msg="Item's position has changed."
context.plone_utils.addPortalMessage(msg)

# XXX/vinsci: portal_status_message refactoring: make these lines a function (need to call it from many form scripts)
#
# Strip form data from request, before traversing (otherwise
# they'll be used again in the template we traverse to).
for key in context.REQUEST.form.keys():
    del context.REQUEST.other[key]
context.REQUEST.form.clear()
# not needed:
# del context.REQUEST.environ['QUERY_STRING']

return state
