## Controlled Python Script "delete_confirmation"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Redirects to the regular vs link integrity confirmation page
##
from Products.CMFPlone.utils import isLinked
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _

if isLinked(context):
    # go ahead with the removal, triggering link integrity...
    # we need to copy the code from 'object_delete' here, since traversing
    # there would yield a (disallowed) GET request without the intermediate
    # confirmation page (see `object_delete.cpy`)
    parent = context.aq_inner.aq_parent
    title = safe_unicode(context.title_or_id())

    try:
        lock_info = context.restrictedTraverse('@@plone_lock_info')
    except AttributeError:
        lock_info = None

    if lock_info is not None and lock_info.is_locked():
        message = _(u'${title} is locked and cannot be deleted.',
            mapping={u'title' : title})
    else:
        parent.manage_delObjects(context.getId())
        message = _(u'${title} has been deleted.',
                    mapping={u'title' : title})
        transaction_note('Deleted %s' % context.absolute_url())

    context.plone_utils.addPortalMessage(message)
    status = 'success'
else:
    # navigate to the regular confirmation page...
    status = 'confirm'

return state.set(status=status)
