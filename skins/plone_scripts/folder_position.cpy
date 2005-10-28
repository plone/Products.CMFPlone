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

from Products.CMFPlone import PloneMessageFactory as _

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

context.plone_utils.reindexOnReorder(context)

msg=_(u'Item\'s position has changed.')
context.plone_utils.addPortalMessage(msg)

context.REQUEST.stripFormData()
return state
