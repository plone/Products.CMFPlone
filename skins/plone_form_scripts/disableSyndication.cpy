## Controller Python Script "disableSyndication"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##title=Disable Syndication for a resource
##parameters=

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import safe_unicode

if context.portal_syndication.isSyndicationAllowed(context):
    context.portal_syndication.disableSyndication(context)
    message=_(u'Syndication disabled')
else:
    message=_(u'Syndication not allowed')

from Products.CMFPlone.utils import transaction_note
transaction_note('%s for %s at %s' % (message, safe_unicode(context.title_or_id()), context.absolute_url()))

context.plone_utils.addPortalMessage(message)
return state

