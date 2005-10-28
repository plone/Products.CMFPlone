## Script (Python) "validate_folder_constraintypes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##title=Validates content publishing
##

from Products.CMFPlone import PloneMessageFactory as _

locallyAllowedTypes = context.REQUEST.get('locallyAllowedTypes', [])
immediatelyAddableTypes = context.REQUEST.get('immediatelyAddableTypes', [])

notFound = [t for t in immediatelyAddableTypes \
                if t not in locallyAllowedTypes]
if notFound:
    msg = _(u'You cannot select a preferred type that is not also in the list of addable types. You have selected ${types}.',
            mapping={u'types' : ', '.join(notFound)})
    state.setError('immediatelyAddableTypes', msg,
                    'validation_immediately_addable_types_too_big')
                    
if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'))
    return state.set(status='failure')
else:
    return state

