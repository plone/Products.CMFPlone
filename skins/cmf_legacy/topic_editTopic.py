## Script (Python) "topic_editTopic"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, RESPONSE, acquireCriteria, title=None, description=None
##title=
##

context.edit(acquireCriteria=acquireCriteria,
             title=title,
             description=description)

RESPONSE.redirect('%s/topic_view' % context.absolute_url())
