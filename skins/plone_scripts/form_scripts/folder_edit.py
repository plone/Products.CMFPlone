## Script (Python) "folder_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=field_title, field_description, choice=' Change ', field_id=''
##title=Edit a folder (Plonized)
##
from Products.CMFPlone import transaction_note
REQUEST=context.REQUEST
destination_url=context.absolute_url()

id=field_id

errors=context.validate_folder_edit()
if REQUEST.has_key('errors'):
    edit_form=getattr(context, context.getTypeInfo().getActionById( 'edit'))
    return edit_form()

title, description=field_title, field_description
context.edit( title=title,
              description=description)

qst='portal_status_message=Folder+changed.'
target_action='folder_contents'

context.rename_object(redirect=0, id=id)

tmsg='/'.join(context.portal_url.getRelativeContentPath(context)[:-1])+'/'+context.title_or_id()+' has been modified.'
transaction_note(tmsg)

REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                        , target_action
                                        , qst
                                        ) )
