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
    edit_form=context.plone_utils.getNextPageFor( context
                                                , script.getId()
                                                , 'failure')
    return edit_form()
    
context.edit(remote_url=remote_url)

context.plone_utils.contentEdit( context
                               , id=id
                               , description=description)

return context.plone_utils.getNextRequestFor( context
                                            , script.getId()
                                            , 'success'
                                            , portal_status_message='Link+changed')

