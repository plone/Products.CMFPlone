## Script (Python) "enableSyndication"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Enable Syndication for a resource
##parameters=

url=''

if context.portal_syndication.isSiteSyndicationAllowed():
  context.portal_syndication.enableSyndication(context)
  url='%s/portal_form/%s?portal_status_message=%s' % ( context.absolute_url(),
                                                       'synPropertiesForm',
                                                       'Syndication+enabled.' )
else:
  url='%s/portal_form/%s?portal_status_message=%s' % ( context.absolute_url(),
                                                       'synPropertiesForm',
                                                       'Syndication+not+allowed.' )

return context.REQUEST.RESPONSE.redirect(url)
