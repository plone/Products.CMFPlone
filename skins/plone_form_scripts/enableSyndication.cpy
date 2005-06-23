## Controller Python Script "enableSyndication"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##title=Enable Syndication for a resource
##parameters=

if context.portal_syndication.isSiteSyndicationAllowed():
    context.portal_syndication.enableSyndication(context)
    message="Syndication enabled"
else:
    message="Syndication not allowed"

from Products.CMFPlone import transaction_note
transaction_note('%s for %s at %s' % (message, context.title_or_id(), context.absolute_url()))

context.plone_utils.addPortalMessage(message)
return state


