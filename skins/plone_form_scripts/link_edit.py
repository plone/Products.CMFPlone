## Script (Python) "link_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=field_remote_url, field_id='', field_title=None, field_description=None, subject=None
##title=Edit a link
##

REQUEST=context.REQUEST
if not field_id:
    field_id=context.getId()
    REQUEST.set('field_id', field_id)

id=field_id
remote_url=field_remote_url

if context.Type().strip()=='Link' and remote_url.find('://')==-1: 
    remote_url='http://'+remote_url

errors=context.validate_link_edit()
if errors:
    edit_form=getattr(context, context.getTypeInfo().getActionById( 'edit'))
    return edit_form()

context.edit(remote_url=remote_url)

qst='?portal_status_message=Link+changed.'
context.REQUEST.set('portal_status_message', 'Link+changed.')

if hasattr(context, 'extended_edit'):
    edit_hook=getattr(context,'extended_edit')
    response=edit_hook(redirect=0)
    if response:
        return response
		
context.rename_object(redirect=0, id=id)

return REQUEST.RESPONSE.redirect( context.absolute_url() + '/link_view' + qst )
