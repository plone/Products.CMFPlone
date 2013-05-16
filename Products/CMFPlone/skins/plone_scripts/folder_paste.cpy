## Controller Python Script "folder_paste"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Paste objects into a folder

from AccessControl import Unauthorized
from logging import getLogger
from OFS.CopySupport import CopyError
from Products.CMFPlone import PloneMessageFactory as _
from ZODB.POSException import ConflictError

msg = _(u'Copy or cut one or more items to paste.')

logger = getLogger("Plone")

if context.cb_dataValid:
    try:
        context.manage_pasteObjects(context.REQUEST['__cp'])
        from Products.CMFPlone.utils import transaction_note
        transaction_note('Pasted content to %s' % (context.absolute_url()))
        context.plone_utils.addPortalMessage(_(u'Item(s) pasted.'))
        return state
    except ConflictError:
        raise
    except ValueError:
        msg = _(u'Disallowed to paste item(s).')
    except Unauthorized:
        msg = _(u'Unauthorized to paste item(s).')
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
    except: # fallback
        if '__cp' not in context.REQUEST:
            msg = _(u'Paste could not find clipboard content.')
        else:
            logger.exception('Exception during pasting')
            msg = _(u'Unknown error occured. Please check your logs')

# raise an Exception to abort the transaction. CMFFormController
# does not do this for us and the objects are already pasted. Otherwise
# we end up in an inconsistent state.
raise Exception(msg)
