## Script (Python) "newsitem_edit"
##parameters=text, text_format, field_title='', field_description='', choice=' Change ', subject=None, field_id=''
##title=Edit a news item
from Products.CMFPlone import transaction_note
REQUEST=context.REQUEST

errors=context.validate_newsitem_edit()
if errors:
    edit_form=getattr(context, context.getTypeInfo().getActionById( 'edit'))
    return edit_form()
qst='portal_status_message=News+Item+changed.'

#XXX eed to call edit after metadata edit or format will be reset to context's text_format
context.edit( text 
            , field_description
            , text_format )

context.plone_utils.contentEdit( context
                               , id=field_id
                               , description=field_description)
#context.rename_object(redirect=0, id=id)
#tmsg='/'.join(context.portal_url.getRelativeContentPath(context)[:-1])+'/'+context.title_or_id()+' has been modified.'
#transaction_note(tmsg)

target_action = context.getTypeInfo().getActionById( 'view' )
context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , target_action
                                                , qst
                                                ) )
