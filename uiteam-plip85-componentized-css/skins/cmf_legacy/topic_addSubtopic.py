## Script (Python) "topic_addSubtopic"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, RESPONSE, new_id
##title=
##

topictype = context.getTypeInfo()
context.addSubtopic(new_id)

action = topictype.getActionById('subtopics')
url = '%s/%s?portal_status_message=%s' % (
    context.absolute_url(),
    action,
    "Subtopic+'%s'+added" % new_id
    )
RESPONSE.redirect(url)
