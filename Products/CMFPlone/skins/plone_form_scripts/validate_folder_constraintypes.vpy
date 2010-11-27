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

currentPrefer = context.REQUEST.get('currentPrefer', [])
currentAllow = context.REQUEST.get('currentAllow', [])

#plone_log=context.plone_log
#plone_log( "VAL: currentAllow=%s, currentPrefer=%s" % ( currentAllow, currentPrefer ))

notFound = [t for t in currentAllow if t not in currentPrefer]
if notFound:
    msg = _(u'You cannot have a type as secondary type without having it allowed. You have selected ${types}.',
            mapping={u'types' : ', '.join(notFound)})
    state.setError('currentPrefer', msg,
                    'validation_immediately_addable_types_too_big')

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    return state

