## Controller Python Script "enableSyndication"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##title=Enable Syndication for a resource
##parameters=

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import safe_unicode

if context.portal_syndication.isSiteSyndicationAllowed():
    context.portal_syndication.enableSyndication(context)
    message=_(u'Syndication enabled')
else:
    message=_(u'Syndication not allowed')

from Products.CMFPlone.utils import transaction_note
transaction_note('%s for %s at %s' % (message, safe_unicode(context.title_or_id()), context.absolute_url()))

context.plone_utils.addPortalMessage(message)
return state
