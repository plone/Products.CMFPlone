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
    context.moveObjectUp(id)

if position.lower()=='down':
    context.moveObjectDown(id)

if position.lower()=='top':
    context.moveObjectToTop(id)

if position.lower()=='bottom':
    context.moveObjectToBottom(id)

# order folder by field
# id in this case is the field    
if position.lower()=='ordered':
    context.orderObjects(id)



response=context.REQUEST.RESPONSE
return response.redirect('%s/%s?portal_status_message=%s' % (context.absolute_url(),
                                                             'folder_contents',
                                                             "Item's position has changed.") )

