## Controlled Python Script "validate_emailaddr"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=email=''
##title=Validates an email
##

member=context.portal_membership.getAuthenticatedMember()
if not member.canWriteProperty('email'):
    return state

from Products.CMFPlone import PloneMessageFactory as _
reg_tool=context.portal_registration

def invalid(field):
    state.setError('email', _(u'You entered an invalid email address.'), 'invalid_email')

if email and reg_tool.isValidEmail(email):
    pass
else:
    invalid('email')

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    return state

