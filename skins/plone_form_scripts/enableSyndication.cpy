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
    portal_status_message="Syndication enabled"
else:
    portal_status_message="Syndication not allowed"

from Products.CMFPlone.utils import transaction_note
transaction_note('%s for %s at %s' % (portal_status_message, context.title_or_id(), context.absolute_url()))

return state.set(portal_status_message=portal_status_message)


