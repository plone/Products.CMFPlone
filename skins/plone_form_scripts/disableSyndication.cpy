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

if context.portal_syndication.isSyndicationAllowed(context):
    context.portal_syndication.disableSyndication(context)
    message='Syndication disabled'
else:
    message='Syndication not allowed'

from Products.CMFPlone.utils import transaction_note
transaction_note('%s for %s at %s' % (message, context.title_or_id(), context.absolute_url()))

context.plone_utils.addPortalMessage(_(message))
return state

