## Script (Python) "topic_editTopic"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, RESPONSE, acquireCriteria, field_id, field_title=None, field_description=None
##title=
##
id, title, description = field_id, field_title, field_description
errors=context.validate_topic_edit()

if errors:
    edit_form=getattr(context, context.getTypeInfo().getActionById( 'edit'))
    return edit_form()

context.edit(acquireCriteria=acquireCriteria,
             title=title,
             description=description)

qst='portal_status_message=Topic+changed.'
target_action = context.getTypeInfo().getActionById( 'view' )

#this needs to be factored into renameAndViewObject and taken out of extrneded_edit
if id!=context.getId():
    container.manage_renameObjects( (context.getId(), ), (id, ))
    url='%s/%s?%s' % ( REQUEST['URL2']
                     , id+'/'+target_action
                     , '/'+qst )
    return REQUEST.RESPONSE.redirect(url)

context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , target_action
                                                , qst) )

#RESPONSE.redirect('%s/topic_view' % context.absolute_url())
