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

response=context.REQUEST.RESPONSE
return response.redirect('%s/%s?portal_status_message=%s' % (context.absolute_url(),
                                                             'folder_contents',
                                                             "Item's position has changed.") )

