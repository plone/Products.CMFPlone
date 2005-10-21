## Script (Python) "undo"
##title=Undo transactions
##parameters=transaction_info, came_from

from Products.CMFPlone import PloneMessageFactory as _
from Products.PythonScripts.standard import url_quote_plus

context.portal_undo.undo(context, transaction_info)

msg=_(u'Transaction(s) undone.')

if came_from.find('?')==-1:
    return context.REQUEST.RESPONSE.redirect( '%s?portal_status_message=%s' % (came_from, url_quote_plus(msg)) )
return context.REQUEST.RESPONSE.redirect(came_from[:came_from.find('?')]+'?portal_status_message='+url_quote_plus(msg))
