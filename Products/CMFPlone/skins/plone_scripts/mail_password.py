## Script (Python) "mail_password"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Mail a user's password
##parameters=

from Products.CMFPlone import PloneMessageFactory as pmf
from AccessControl import Unauthorized
REQUEST=context.REQUEST
try:
    response = context.portal_registration.mailPassword(REQUEST['userid'], REQUEST)
except ValueError, e:
    try:
        msg = pmf(e.message)
    except Unauthorized:
        try:
            msg = pmf(str(e))
        except Unauthorized:
            # If we are not allowed to tell the user, what is wrong, he
            # should get an error message and contact the admins
            raise e
    context.plone_utils.addPortalMessage(msg)
    response = context.mail_password_form()
return response
