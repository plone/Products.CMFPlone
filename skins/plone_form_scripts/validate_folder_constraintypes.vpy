## Script (Python) "validate_folder_constraintypes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##title=Validates content publishing
##

locallyAllowedTypes = context.REQUEST.get('locallyAllowedTypes', [])
immediatelyAddableTypes = context.REQUEST.get('immediatelyAddableTypes', [])

notFound = [t for t in immediatelyAddableTypes \
                if t not in locallyAllowedTypes]
if notFound:
    state.setError('immediatelyAddableTypes', 
                    'You cannot select a preferred type that is not ' \
                    'also in the list of addable types. You have selected %s.' \
                      % ','.join(notFound),
                    'validation_immediately_addable_types_too_big')
                    
if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state

