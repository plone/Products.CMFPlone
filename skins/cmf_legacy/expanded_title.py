## Script (Python) "expanded_title"
##parameters=
##title=Build title which includes site title
##
site_title = context.portal_url.getPortalObject().Title()
page_title = context.Title()

if page_title != site_title:
   page_title = site_title + ": " + page_title

return page_title
