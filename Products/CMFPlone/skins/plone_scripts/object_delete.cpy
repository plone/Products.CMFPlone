## Controller Python Script "object_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Delete objects from a folder
##

from AccessControl import Unauthorized
from zExceptions import Forbidden
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _

REQUEST = context.REQUEST
if REQUEST.get('REQUEST_METHOD', 'GET').upper() == 'GET':
    raise Unauthorized, 'This method can not be accessed using a GET request'

parent = context.aq_inner.aq_parent
title = safe_unicode(context.title_or_id())

try:
    lock_info = context.restrictedTraverse('@@plone_lock_info')
except AttributeError:
    lock_info = None

if lock_info is not None and lock_info.is_locked():
    message = _(u'${title} is locked and cannot be deleted.',
            mapping={u'title' : title})
    context.plone_utils.addPortalMessage(message, type='error')
    return state.set(status = 'failure')
else:
    authenticator = context.restrictedTraverse('@@authenticator', None)
    if not authenticator.verify():
        raise Forbidden
    parent.manage_delObjects(context.getId())
    message = _(u'${title} has been deleted.',
                mapping={u'title' : title})
    transaction_note('Deleted %s' % context.absolute_url())
    context.plone_utils.addPortalMessage(message)
    return state.set(status = 'success')
