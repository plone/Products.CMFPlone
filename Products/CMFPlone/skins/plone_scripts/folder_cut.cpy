## Controller Python Script "folder_cut"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Cut objects from a folder and copy to the clipboard

from OFS.CopySupport import CopyError
from Products.CMFCore.exceptions import ResourceLockedError
from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _

REQUEST = context.REQUEST
if 'paths' in REQUEST:
    ids = [p.split('/')[-1] or p.split('/')[-2] for p in REQUEST['paths']]

    try:
        context.manage_cutObjects(ids, REQUEST)
    except CopyError:
        message = _(u'One or more items not moveable.')
        context.plone_utils.addPortalMessage(message, 'error')
        return state.set(status='failure')
    except AttributeError:
        message = _(u'One or more selected items is no longer available.')
        context.plone_utils.addPortalMessage(message, 'error')
        return state.set(status='failure')
    except ResourceLockedError:
        message = _(u'One or more selected items is locked.')
        context.plone_utils.addPortalMessage(message, 'error')
        return state.set(status='failure')

    transaction_note('Cut %s from %s' % ((str(ids)), context.absolute_url()))
    message = _(u'${count} item(s) cut.', mapping={u'count': len(ids)})

    context.plone_utils.addPortalMessage(message)
    return state

context.plone_utils.addPortalMessage(
    _(u'Please select one or more items to cut.'), 'error')
return state.set(status='failure')
