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

from Products.CMFPlone import transaction_note
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
    context.plone_utils.addPortalMessage(message)
    return state.set(status = 'failure')

message = context.translate("${title} copied.",
                            {'title': context.title_or_id()})
transaction_note('Copied object %s' % context.absolute_url())


context.plone_utils.addPortalMessage(message)
return state.set(status = 'success')
