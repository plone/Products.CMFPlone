## Script (Python) "undo"
##title=Undo transactions
##parameters=transaction_info, came_from
context.portal_undo.undo(context, transaction_info)
msg='portal_status_message=Transaction(s)+undone'
if came_from.find('?')==-1:
    return context.REQUEST.RESPONSE.redirect( '%s?%s' % (came_from, msg) )
return context.REQUEST.RESPONSE.redirect(came_from[:came_from.find('?')]+'?'+msg)
