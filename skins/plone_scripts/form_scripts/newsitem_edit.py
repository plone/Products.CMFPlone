## Script (Python) "newsitem_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=text, text_format, title='', description='', choice=' Change ', subject=None, id=''
##title=Edit a news item

errors=context.portal_form_validation.validate(context, 'validate_newsitem_edit')
if errors:
    edit_form=getattr(context, context.getTypeInfo().getActionById( 'edit'))
    return edit_form()

context.edit( text 
            , description
            , text_format )

context.plone_utils.contentEdit( context
                               , id=id
                               , description=description)

message='portal_status_message=News+Item+changed.'

context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , context.getTypeInfo().getActionById( 'view' )
                                                , message) )
