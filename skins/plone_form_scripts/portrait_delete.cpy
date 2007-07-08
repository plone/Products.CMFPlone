## Controller Python Script "personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Personalization Handler.

from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _

member=context.portal_membership.getAuthenticatedMember()

context.portal_membership.deletePersonalPortrait(member.getId())

tmsg='Deleted portrait for %s' % (member.getId())
transaction_note(tmsg)

context.plone_utils.addPortalMessage(_(u'Your portrait has been deleted.'))
return state
