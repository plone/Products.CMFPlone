## Script (Python) "folder_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=field_title, field_description, choice=' Change ', field_id=''
##title=Edit a folder (Plonized)
##

errors=context.validate_folder_edit()
if errors:
    edit_form=getattr(context, context.getTypeInfo().getActionById( 'edit'))
    return edit_form()

context.edit( title=field_title,
              description=field_description)

context.plone_utils.contentEdit( context
                               , id=field_id
                               , description=field_description)

qst='portal_status_message=Folder+changed.'

context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                        , 'folder_contents'
                                        , qst
                                        ) )
