## Controller Python Script "login_change_password"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=password
##title=Change a user's password upon initial login
##

from Products.CMFPlone import PloneMessageFactory as _

mt = context.portal_membership
member=mt.getAuthenticatedMember()
try:
    mt.setPassword(password, REQUEST=context.REQUEST)
except AttributeError:
    context.plone_utils.addPortalMessage(_(u'While changing your password an AttributeError occurred. This is usually caused by your user being defined outside the portal.'), 'error')
    return state.set(status='failure')

member.setProperties(must_change_password=0)

from Products.CMFPlone.utils import transaction_note
transaction_note('Changed password for %s' % (member.getUserName()))

return state
