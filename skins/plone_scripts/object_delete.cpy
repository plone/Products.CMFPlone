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

from Products.CMFPlone import transaction_note
from Products.CMFPlone import PloneMessageFactory as _

REQUEST = context.REQUEST

parent = context.aq_inner.aq_parent
parent.manage_delObjects(context.getId())

message = _(u'${title} has been deleted.',
            mapping={u'title': context.title_or_id()})
transaction_note('Deleted %s' % context.absolute_url())

return state.set(status = 'success', portal_status_message = message)
