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
    edit_form=getattr(context, context.getTypeInfo().getActionById( 'edit'))
    return edit_form()

context.edit(acquireCriteria=acquireCriteria,
             title=title,
             description=description)

context.plone_utils.contentEdit( context
                               , id=id
                               , description=description)
	     
qst='portal_status_message=Topic+changed.'

context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , context.getTypeInfo().getActionById( 'view' )
                                                , qst) )
