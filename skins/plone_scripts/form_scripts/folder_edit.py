## Script (Python) "folder_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=title, description, choice=' Change ', id=''
##title=Edit a folder (Plonized)
##
new_context = context.portal_factory.doCreate(context, id)
new_context.edit( title=title
                , description=description)
new_context.plone_utils.contentEdit( context
                                   , id=id
                                   , description=description)
return ('success', new_context)
