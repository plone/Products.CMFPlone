## Script (Python) "newsitem_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=text, text_format, title='', description='', choice=' Change ', subject=None, id=''
##title=Edit a news item

new_context = context.portal_factory.doCreate(context,id)
new_context.edit( text 
                , description
                , text_format )
new_context.plone_utils.contentEdit( context
                                   , id=id
                                   , description=description)
return ('success', new_context, {'portal_status_message':context.REQUEST.get('portal_status_message', 'News item changes saved.')})

