## Script (Python) "topic_addCriterion"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, RESPONSE, field, criterion_type
##title=
##

context.addCriterion(field=field, criterion_type=criterion_type)

RESPONSE.redirect('%s/topic_criteria_form' % context.absolute_url())
