## Script (Python) "disableSyndication"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Disable Syndication for a resource
##parameters=

url = ''

if context.portal_syndication.isSyndicationAllowed(context):
  context.portal_syndication.disableSyndication(context)
  url='%s/portal_form/%s?portal_status_message=%s' % ( context.absolute_url(),
                                                       'synPropertiesForm',
                                                       'Syndication+disabled.' )
else:
  url='%s/portal_form/%s?portal_status_message=%s' % ( context.absolute_url(),
                                                       'synPropertiesForm',
                                                       'Syndication+not+allowed.' )

return context.REQUEST.RESPONSE.redirect(url)
