## Script (Python) "topic_editCriteria"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, RESPONSE, criteria
##title=
##
"""\
Save changes to the list of criteria.  This is done by going over
the submitted criteria records and comparing them against the
criteria object's editable attributes.  A 'command' object is
built to send to the Criterion objects 'apply' method, which in turn
applies the command to the Criterion objects 'edit' method.
"""

for rec in criteria:
    crit = context.getCriterion(rec.id)
    command = {}
    for attr in crit.editableAttributes():
        tmp = getattr(rec, attr, None)
        # Due to having multiple radio buttons on the same page
        # with the same name but belonging to different records,
        # they needed to be associated with different records with ids
        if tmp is None:
            tmp = getattr(rec, '%s__%s' % (attr, rec.id), None)
        command[attr] = tmp
    crit.apply(command)

message='Changes+saved.'
RESPONSE.redirect('%s/topic_criteria_form?portal_status_message=%s' % (
    context.absolute_url(), message)
                  )

