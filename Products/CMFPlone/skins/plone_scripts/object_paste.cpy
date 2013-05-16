## Controller Python Script "object_paste"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Paste objects into the parent/this folder

from AccessControl import Unauthorized
from logging import getLogger
from OFS.CopySupport import CopyError
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import transaction_note
from ZODB.POSException import ConflictError

if not context.cb_dataValid():
    msg = _(u'Copy or cut one or more items to paste.')
    context.plone_utils.addPortalMessage(msg, 'error')
    return state.set(status='failure')

ok = True

logger = getLogger("Plone")

try:
    context.manage_pasteObjects(context.REQUEST['__cp'])
except ConflictError:
    raise
except Unauthorized:
    # avoid this unfriendly exception text:
    # "You are not allowed to access 'manage_pasteObjects' in this context"
    msg = _(u'You are not authorized to paste here.')
    ok = False
except CopyError as e:
    error_string = str(e)
    if 'Item Not Found' in error_string:
        context.plone_utils.addPortalMessage(
            _(u'The item you are trying to paste could not be found. '
               'It may have been moved or deleted after you copied or cut it. '),
            'error',
        )
        return state.set(status='failure')
    raise
except Exception as e:
    if '__cp' in context.REQUEST:
        logger.exception('Exception during pasting')
    msg = e
    ok = False

if ok:
    transaction_note('Pasted content to %s' % (context.absolute_url()))
    context.plone_utils.addPortalMessage(_(u'Item(s) pasted.'))
    return state.set(status='success')
else:
    # raise an Exception to abort the transaction. CMFFormController
    # does not do this for us and the objects are already pasted. Otherwise
    # we end up in an inconsistent state.
    raise Exception(msg)
