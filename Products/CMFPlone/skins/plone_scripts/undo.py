## Script (Python) "undo"
##title=Undo transactions
##parameters=transaction_info, came_from

from Products.CMFPlone import PloneMessageFactory as _

context.portal_undo.undo(context, transaction_info)
context.plone_utils.addPortalMessage(_(u'Transaction(s) undone.'))

return context.REQUEST.RESPONSE.redirect(came_from)
