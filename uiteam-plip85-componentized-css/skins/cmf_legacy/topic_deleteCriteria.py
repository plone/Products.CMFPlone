## Script (Python) "topic_deleteCriteria"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, RESPONSE, criterion_ids
##title=
##

for cid in criterion_ids:
    context.deleteCriterion(cid)

message = 'Criteria+deleted.'
RESPONSE.redirect('%s/topic_criteria_form?portal_status_message=%s' % (
    context.absolute_url(), message)
                  )
