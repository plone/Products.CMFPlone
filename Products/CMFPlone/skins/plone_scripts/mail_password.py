## Script (Python) "mail_password"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Mail a user's password
##parameters=

from Products.CMFPlone import PloneMessageFactory as pmf
REQUEST=context.REQUEST
try:
    response = context.portal_registration.mailPassword(REQUEST['userid'], REQUEST)
except ValueError, e:
    context.plone_utils.addPortalMessage(pmf(str(e)))
    response = context.mail_password_form()
return response
