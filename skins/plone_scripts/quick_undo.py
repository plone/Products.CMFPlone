## Script (Python) "quick_undo"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Undo transactions
##parameters=

from Products.CMFPlone import PloneMessageFactory as _
from Products.PythonScripts.standard import url_quote_plus
from AccessControl import Unauthorized

request=context.REQUEST
trxs=context.portal_undo.listUndoableTransactionsFor(context)

if trxs:
    tran_id = trxs[0]['id']
    context.portal_undo.undo(context, (tran_id,) )

msg=_(u'Transaction undone.')
came_from = request.get('came_from', request['HTTP_REFERER'])

pieces = context.plone_utils.urlparse(came_from)
path = pieces[2].split('/')[1:]

if '?' in came_from:
    came_from=came_from[:came_from.index('?')]

try:
    o = context.portal_url.getPortalObject().restrictedTraverse(path)
except (Unauthorized, KeyError, AttributeError):
    came_from=context.portal_url()

return request.RESPONSE.redirect('%s?portal_status_message=%s' % (came_from, url_quote_plus(msg)))
