## Controller Python Script "folder_position"
##title=Move objects in a ordered folder
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=position='ordered', id=None, template_id='folder_contents', delta=1, reverse=None

from Products.CMFPlone import PloneMessageFactory as _
delta = int(delta)

position = position.lower()

if position == 'up':
    context.moveObjectsUp(id, delta=delta)
elif position == 'down':
    context.moveObjectsDown(id, delta=delta)
elif position == 'top':
    context.moveObjectsToTop(id)
elif position == 'bottom':
    context.moveObjectsToBottom(id)
# order folder by field
# id in this case is the field
elif position == 'ordered':
    context.orderObjects(id, reverse)

context.plone_utils.reindexOnReorder(context)

msg = _(u'Item\'s position has changed.')
context.plone_utils.addPortalMessage(msg)

return state
