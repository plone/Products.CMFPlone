## Script (Python) "newsitem_edit"
##parameters=text, text_format, field_title='', description='', choice=' Change ', subject=None
##title=Edit a news item
REQUEST=context.REQUEST

errors=context.validate_newsitem_edit()
if errors:
    edit_form=getattr(context, context.getTypeInfo().getActionById( 'edit'))
    return edit_form()

context.edit( text 
            , description
	    , text_format )

REQUEST.set('title', field_title)

REQUEST.set('portal_status_message', 'News+Item+changed.')
qst='portal_status_message=News+Item+changed.'
if hasattr(context, 'extended_edit'):
    edit_hook=getattr(context, 'extended_edit')
    response=edit_hook()
    if response:
        return response

target_action = context.getTypeInfo().getActionById( 'view' )

context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , target_action
                                                , qst
                                                ) )
