## Script (Python) "folder_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=title, description, choice=' Change ', id=''
##title=Edit a folder (Plonized)
##

errors=context.portal_form_validation.validate(context, 'validate_folder_edit')
if errors:
    edit_form=context.portal_navigation.getNextPageFor( context
                                                , script.getId()
                                                , 'failure')
    return edit_form()

context.edit( title=title,
              description=description)

context.plone_utils.contentEdit( context
                               , id=id
                               , description=description)

return context.portal_navigation.getNextRequestFor( context
                                            , script.getId()
                                            , 'success'
                                            , portal_status_message='Folder changed.' )
