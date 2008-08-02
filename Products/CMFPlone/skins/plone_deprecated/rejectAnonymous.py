## Script (Python) "rejectAnonymous"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from Products.CMFPlone import PloneMessageFactory as _

context.plone_log("The rejectAnonymous script is deprecated and will be "
                  "removed in Plone 4.0.")

if context.portal_membership.isAnonymousUser():

    url = '%s/login_form' % context.portal_url()
    context.plone_utils.addPortalMessage(_(u'You must sign in first.'))

    RESPONSE=context.REQUEST.RESPONSE
    return RESPONSE.redirect(url)
return True
