## Script (Python) "topic_editTopic"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, RESPONSE, acquireCriteria, id, title=None, description=None
##title=
##

errors=context.portal_form_validation.validate(context, 'validate_topic_edit')
if errors:
    edit_form=context.plone_utils.getNextPageFor( context
                                                , script.getId()
                                                , 'failure' )
    return edit_form()

context.edit(acquireCriteria=acquireCriteria,
             title=title,
             description=description)

context.plone_utils.contentEdit( context
                               , id=id
                               , description=description)

return context.plone_utils.getNextRequestFor( context
                                            , script.getId()
                                            , 'success'
                                            , portal_status_message='Topic changed.')
