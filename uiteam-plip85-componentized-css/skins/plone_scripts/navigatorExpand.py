## Script (Python) "navigatorExpand"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=topic
##title=navigatorExpand
##
session = context.REQUEST.SESSION
referer = context.REQUEST['HTTP_REFERER']

session.set('navExpand',topic)

return context.REQUEST.RESPONSE.redirect(referer)
