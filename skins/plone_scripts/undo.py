## Script (Python) "undo"
##title=Undo transactions
##parameters=transaction_info, came_from
context.portal_undo.undo(context, transaction_info)
return context.REQUEST.RESPONSE.redirect( '%s?%s' % (came_from ,'portal_status_message=Transaction(s)+undone' ) )
