## Script (Python) "link_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=remote_url, id='', title=None, description=None, subject=None
##title=Edit a link
##

errors = context.portal_form_validation.validate(context, 'validate_link_edit')
if errors:
    edit_form=getattr(context, context.getTypeInfo().getActionById( 'edit'))
    return edit_form()

context.edit(remote_url=remote_url)

context.plone_utils.contentEdit( context
                               , id=id
                               , description=description)

qst='?portal_status_message=Link+changed.'

return context.REQUEST.RESPONSE.redirect( context.absolute_url()
                                          + '/link_view'
                                          + qst )
