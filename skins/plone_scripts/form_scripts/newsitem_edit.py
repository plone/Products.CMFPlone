## Script (Python) "newsitem_edit"
##parameters=text, text_format, field_title='', field_description='', choice=' Change ', subject=None, field_id=''
##title=Edit a news item
from Products.CMFPlone import transaction_note
REQUEST=context.REQUEST
if not field_id:
    field_id=context.getId()
    REQUEST.set('field_id', field_id)
id,description = field_id, field_description

errors=context.validate_newsitem_edit()

if REQUEST.has_key('errors'):
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

#XXX need to call edit after metadata edit or format will be reset to context's text_format
context.edit( text 
            , description
            , text_format )

if id!=context.getId():
    context.rename_object(redirect=0, id=id)

tmsg='/'.join(context.portal_url.getRelativeContentPath(context)[:-1])+'/'+context.title_or_id()+' has been modified.'
transaction_note(tmsg)
target_action = context.getTypeInfo().getActionById( 'view' )
context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , target_action
                                                , qst
                                                ) )
