## Script (Python) "newsitem_edit"
##parameters=text, text_format, field_title='', description='', choice=' Change ', subject=None, field_id=''
##title=Edit a news item
REQUEST=context.REQUEST
if not field_id:
    field_id=context.getId()
    REQUEST.set('field_id', field_id)
id = field_id

errors=context.validate_newsitem_edit()

if errors:
    edit_form=getattr(context, context.getTypeInfo().getActionById( 'edit'))
    return edit_form()

REQUEST.set('title', field_title)
REQUEST.set('portal_status_message', 'News+Item+changed.')
qst='portal_status_message=News+Item+changed.'
if hasattr(context, 'extended_edit'):
    edit_hook=getattr(context, 'extended_edit')
    response=edit_hook()
    if response:
        return response

context.edit( text  #XXX need to call edit after metadata edit or format will be reset to context's text_format
            , description
            , text_format )

if id!=context.getId():
    context.rename_object(redirect=0, id=id)

target_action = context.getTypeInfo().getActionById( 'view' )
context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , target_action
                                                , qst
                                                ) )
