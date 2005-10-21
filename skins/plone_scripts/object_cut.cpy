## Controller Python Script "object_cut"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Cut a object to the clipboard
##

from Products.CMFPlone import transaction_note
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from OFS.CopySupport import CopyError
from AccessControl import Unauthorized

REQUEST = context.REQUEST

mtool = getToolByName(context, 'portal_membership')
if not mtool.checkPermission('Copy or Move', context):
    msg = _(u'Permission denied to cut ${title}.',
            mapping={u'title' : context.title_or_id()})
    raise Unauthorized, msg

parent = context.aq_inner.aq_parent
try:
    parent.manage_cutObjects(context.getId(), REQUEST)
except CopyError:
    message = _(u'${title} is not moveable.',
                mapping={u'title' : context.title_or_id()})
    return state.set(status = 'failure', portal_status_message = message)

message = _(u'${title} cut.', mapping={u'title' : context.title_or_id()})
transaction_note('Cut object %s' % context.absolute_url())

return state.set(status = 'success', portal_status_message = message)
