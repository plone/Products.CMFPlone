## Script (Python) "plone_change_password"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Action to change password
##parameters=password, password_confirm, current, domains=None

from Products.CMFPlone import PloneMessageFactory as _

REQUEST = context.REQUEST
if 'cancel' in REQUEST.form:
    context.plone_utils.addPortalMessage(_(u'Password change was canceled.'),
                                         'warning')
    return context.REQUEST.RESPONSE.redirect(
            '%s/@@personal-preferences' % context.absolute_url())

mt = context.portal_membership

if not mt.testCurrentPassword(current):
    failMessage = _(u'Does not match current password.')
    context.plone_utils.addPortalMessage(failMessage, 'error')
    return context.password_form(context,
                                 REQUEST,
                                 error=failMessage)

failMessage = context.portal_registration \
                    .testPasswordValidity(password, password_confirm)
if failMessage:
    context.plone_utils.addPortalMessage(failMessage, 'error')
    return context.password_form(context,
                                 REQUEST,
                                 error=failMessage)

member = mt.getAuthenticatedMember()
try:
    mt.setPassword(password, domains, REQUEST=context.REQUEST)
except AttributeError:
    failMessage = _(u'While changing your password an AttributeError '
                    u'occurred. This is usually caused by your user being '
                    u'defined outside the portal.')
    context.plone_utils.addPortalMessage(failMessage, 'error')
    return context.password_form(context,
                                 REQUEST,
                                 error=failMessage)

from Products.CMFPlone.utils import transaction_note
transaction_note('Changed password for %s' % (member.getUserName()))

context.plone_utils.addPortalMessage(_(u'Password changed.'))

return context.REQUEST.RESPONSE.redirect(
            '%s/@@personal-preferences' % context.absolute_url())
