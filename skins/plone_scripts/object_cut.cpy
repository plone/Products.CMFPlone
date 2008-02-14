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

from Products.CMFPlone.utils import transaction_note
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone import PloneMessageFactory as _
from OFS.CopySupport import CopyError
from AccessControl import Unauthorized

REQUEST = context.REQUEST
title = safe_unicode(context.title_or_id())

mtool = getToolByName(context, 'portal_membership')
if not mtool.checkPermission('Copy or Move', context):
    msg = _(u'Permission denied to cut ${title}.',
            mapping={u'title' : title})
    raise Unauthorized, msg

try:
    lock_info = context.restrictedTraverse('@@plone_lock_info')
except AttributeError:
    lock_info = None

if lock_info is not None and lock_info.is_locked():
    message = _(u'${title} is locked and cannot be cut.',
                mapping={u'title' : title})
    context.plone_utils.addPortalMessage(message, 'error')
    return state.set(status = 'failure')

parent = context.aq_inner.aq_parent
try:
    parent.manage_cutObjects(context.getId(), REQUEST)
except CopyError:
    message = _(u'${title} is not moveable.',
                mapping={u'title' : title})
    context.plone_utils.addPortalMessage(message, 'error')
    return state.set(status = 'failure')

message = _(u'${title} cut.', mapping={u'title' : title})
transaction_note('Cut object %s' % context.absolute_url())

context.plone_utils.addPortalMessage(message)
return state.set(status = 'success')
