## Python Script "folder_position"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=position, id
##title=Move objects in a ordered folder
##

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



response=context.REQUEST.RESPONSE
return response.redirect('%s/%s?portal_status_message=%s' % (context.absolute_url(),
                                                             'folder_contents',
                                                             "Item's position has changed.") )

