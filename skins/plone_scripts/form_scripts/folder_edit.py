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
    edit_form=getattr(context, context.getTypeInfo().getActionById( 'edit'))
    return edit_form()

context.edit( title=title,
              description=description)

context.plone_utils.contentEdit( context
                               , id=id
                               , description=description)

qst='portal_status_message=Folder+changed.'

context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                        , 'folder_contents'
                                        , qst
                                        ) )
