## Script (Python) "topic_editTopic"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, RESPONSE, acquireCriteria, field_id, field_title=None, field_description=None
##title=
##
REQUEST=context.REQUEST
if not field_id:
    field_id=context.getId()
id, title, description = field_id, field_title, field_description

errors=context.validate_topic_edit()
if REQUEST.has_key('errors'):
    edit_form=getattr(context, context.getTypeInfo().getActionById( 'edit'))
    return edit_form()

context.edit(acquireCriteria=acquireCriteria,
             title=title,
             description=description)
	     
context.rename_object(redirect=0, id=id)

qst='portal_status_message=Topic+changed.'
target_action = context.getTypeInfo().getActionById( 'view' )
context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , target_action
                                                , qst) )
