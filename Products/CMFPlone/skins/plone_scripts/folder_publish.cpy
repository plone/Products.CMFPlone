## Controller Python Script "folder_publish"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=workflow_action=None, paths=[], comment='No comment', expiration_date=None, effective_date=None, include_children=False
##title=Publish objects from a folder
##

from ZODB.POSException import ConflictError
from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _

plone_utils=context.plone_utils
REQUEST=context.REQUEST

if workflow_action is None:
    context.plone_utils.addPortalMessage(_(u'You must select a publishing action.'), 'error')
    return state.set(status='failure')
if not paths:
    context.plone_utils.addPortalMessage(_(u'You must select content to change.'), 'error')
    return state.set(status='failure')

failed = plone_utils.transitionObjectsByPaths(workflow_action, paths, comment,
                                              expiration_date, effective_date,
                                              include_children, REQUEST=REQUEST)

transaction_note( str(paths) + ' transitioned ' + workflow_action )

# It is necessary to set the context to override context from content_status_modify
context.plone_utils.addPortalMessage(_(u'Item state changed.'))
return state.set(context=context)
