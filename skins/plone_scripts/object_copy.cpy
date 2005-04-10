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

REQUEST = context.REQUEST

parent = context.aq_inner.aq_parent
parent.manage_copyObjects(context.getId(), REQUEST)

message = context.title_or_id() + ' copied.'
transaction_note('Copied object %s' % context.absolute_url())


return state.set(status = 'success', portal_status_message = message)
