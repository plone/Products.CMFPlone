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
from Products.CMFCore.utils import getToolByInterfaceName
from Products.CMFPlone import PloneMessageFactory as _
from OFS.CopySupport import CopyError
from AccessControl import Unauthorized

REQUEST = context.REQUEST

mtool = getToolByInterfaceName('Products.CMFCore.interfaces.IMembershipTool')
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
    context.plone_utils.addPortalMessage(message, 'error')
    return state.set(status = 'failure')

message = _(u'${title} cut.', mapping={u'title' : context.title_or_id()})
transaction_note('Cut object %s' % context.absolute_url())

context.plone_utils.addPortalMessage(message)
return state.set(status = 'success')
