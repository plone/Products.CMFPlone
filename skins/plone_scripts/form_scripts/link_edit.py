## Script (Python) "link_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=remote_url, id='', title=None, description=None, subject=None
##title=Edit a link
##

# if there is no id specified, keep the current one
if not id:
    id = context.getId()

new_context = context.portal_factory.doCreate(context, id)
new_context.edit(remote_url=remote_url)
new_context.plone_utils.contentEdit(new_context
                               , id=id
                               , description=description)
return ('success', new_context, {'portal_status_message':context.REQUEST.get('portal_status_message', 'Link changes saved.')})