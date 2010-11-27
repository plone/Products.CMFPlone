## Script (Python) "rssAllowed"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=site=False
##title=RSS Allowed

# this is a replacement for the old syndication allowed option
# in this case we don't bother getting syndication on each folder
# we just check globally
from Products.CMFCore.utils import getToolByName

ps = getToolByName(context, "portal_syndication")

allowed = True
if not site and not ps.isSyndicationAllowed(context):
    allowed = False
if site and not ps.isSiteSyndicationAllowed():
    allowed = False
# really we should be raising an HTTP error, something that
# rss news readers would understand
if not allowed:
    raise ValueError, "Site syndication via RSS feeds is not allowed. Ask the sites"\
    " system administrator to go to portal_syndication > Policies and enable syndication. Each folder"\
    " then needs to have syndication enabled."

