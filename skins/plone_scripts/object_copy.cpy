## Controller Python Script "object_copy"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Copy object from a folder to the clipboard
##

from Products.CMFPlone.utils import transaction_note
from Products.CMFCore.utils import getToolByName
from OFS.CopySupport import CopyError
from AccessControl import Unauthorized

REQUEST = context.REQUEST

mtool = getToolByName(context, 'portal_membership')
if not mtool.checkPermission('Copy or Move', context):
    raise Unauthorized, context.translate("Permission denied to copy ${title}.",
                                          {'title': context.title_or_id()})

parent = context.aq_inner.aq_parent
try:
    parent.manage_copyObjects(context.getId(), REQUEST)
except CopyError:
    message = context.translate("${title} is not copyable.",
                                {'title': context.title_or_id()})
    return state.set(status = 'failure', portal_status_message = message)

message = context.translate("${title} copied.",
                            {'title': context.title_or_id()})
transaction_note('Copied object %s' % context.absolute_url())


return state.set(status = 'success', portal_status_message = message)
