## Controlled Python Script "validate_topic_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validates a topic edit_form contents
##
if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
return state
