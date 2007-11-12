## Controller Python Script "link_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=remote_url, id='', title=None, description=None, subject=None
##title=Edit a link
##

from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _

# if there is no id specified, keep the current one
if not id:
    id = context.getId()

new_context = context.portal_factory.doCreate(context, id)
new_context.edit(remote_url=remote_url)
new_context.plone_utils.contentEdit(new_context,
                                    id=id,
                                    title=title,
                                    description=description)

transaction_note('Edited link %s at %s' % (new_context.title_or_id(), new_context.absolute_url()))

context.plone_utils.addPortalMessage(_(u'Link changes saved.'))
return state.set(context=new_context)
