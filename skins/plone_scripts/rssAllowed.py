# this is a replacement for the old syndication allowed option
# in this case we don't bother getting syndication on each folder
# we just check globally
from Products.CMFCore.utils import getToolByName

ps = getToolByName(context, "portal_syndication")


# if you want the old behaviour, swap the two lines around...
if not ps.isSyndicationAllowed(context):
#if not ps.isSiteSyndicationAllowed():
# really we should be raising an HTTP error, something that
# rss news readers would understand
    raise ValueError, "Site syndication via RSS feeds is not allowed. Ask the sites"\
    " system administrator to go to portal_syndication > Policies and enable syndication. Each folder"\
    " then needs to have syndication enabled."

# this is the backwards compatible response
# assuming that you have rssDisabled (which Plone sites don't actually have)
#    return context.REQUEST.RESPONSE.redirect('%s/rssDisabled?# portal_status_message=Syndication+is+Disabled' % context.absolute_url())
