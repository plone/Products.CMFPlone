## Controller Python Script "validate_personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=email=''
##title=validates user preferences

from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

portal = getToolByName(context, 'portal_url').getPortalObject()
props = getToolByName(portal, 'portal_properties').site_properties
if props.getProperty('use_email_as_login'):
    # Check the validity of the email address as a login name.
    reg_tool = getToolByName(portal, 'portal_registration')
    membership_tool = getToolByName(portal, 'portal_membership')

    username = ''
    if not email:
        state.setError(
            'email',
            _(u'This field is required, please provide some information.'),
            'input_required')
    else:
        username = email

    if not state.getError('email'):
        # Email address is valid, but it is valid as login name?
        member = membership_tool.getAuthenticatedMember()
        # Keeping your email the same (which happens when you change
        # something else on the personalize form) or changing it back to
        # your login name, is fine.
        if email not in (member.getId(), member.getProperty('email')):
            try:
                id_allowed = reg_tool.isMemberIdAllowed(username)
            except Unauthorized:
                state.setError(
                    'email',
                    _('message_email_cannot_change',
                      u"Sorry, you are not allowed to change your email address."),
                    'message_email_cannot_change')
            else:
                if not id_allowed:
                    state.setError(
                        'email',
                        _('message_email_in_use',
                          u"The email address you selected is already in use "
                          "or is not valid as login name. Please choose "
                          "another."),
                        'message_email_in_use')

    if not state.getError('email'):
        # All checks have been done, so finally we can safely signal
        # that this email is the new username.
        context.REQUEST.set('username', email)

if state.getErrors():
    portal.plone_utils.addPortalMessage(
        _(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')

return state
