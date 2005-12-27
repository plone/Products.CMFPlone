## Script (Python) "plone_change_password"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Action to change password
##parameters=password, password_confirm, current, domains=None

from Products.CMFPlone import PloneMessageFactory as _
from Products.PythonScripts.standard import url_quote_plus

REQUEST=context.REQUEST
if REQUEST.form.has_key('cancel'):
    context.plone_utils.addPortalMessage(_(u'Password change was canceled.'))
    return context.plone_memberprefs_panel()

mt=context.portal_membership

if not mt.testCurrentPassword(current):
    failMessage=_(u'Does not match current password.')
    context.plone_utils.addPortalMessage(failMessage)
    return context.password_form(context,
                                 REQUEST,
                                 error=failMessage)

failMessage=context.portal_registration.testPasswordValidity(password, password_confirm)
if failMessage:
    context.plone_utils.addPortalMessage(failMessage)
    return context.password_form(context,
                                 REQUEST,
                                 error=failMessage)

member=mt.getAuthenticatedMember()
try:
    mt.setPassword(password, domains)
except AttributeError:
    failMessage=_(u'While changing your password an AttributeError occurred. This is usually caused by your user being defined outside the portal.')
    context.plone_utils.addPortalMessage(failMessage)
    return context.password_form(context,
                                 REQUEST,
                                 error=failMessage)

#mt.credentialsChanged(password) now in setPassword

from Products.CMFPlone.utils import transaction_note
transaction_note('Changed password for %s' % (member.getUserName()))

msg = _(u'Password changed.')
url='%s/plone_memberprefs_panel?portal_status_message=%s' % ( context.absolute_url(), url_quote_plus(msg) )

return context.REQUEST.RESPONSE.redirect(url)
