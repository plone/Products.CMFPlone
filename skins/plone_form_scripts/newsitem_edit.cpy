## Controller Python Script "newsitem_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=text, text_format, title='', description='', subject=None, id=''
##title=Edit a news item
##

from Products.CMFPlone import PloneMessageFactory as _

# if there is no id specified, keep the current one
if not id:
    id = context.getId()

new_context = context.portal_factory.doCreate(context,id)
new_context.edit( text, description, text_format )
new_context.plone_utils.contentEdit( new_context
                                   , id=id
                                   , title=title
                                   , description=description)

from Products.CMFPlone.utils import transaction_note
transaction_note('Edited news item %s at %s' % (new_context.title_or_id(), new_context.absolute_url()))

context.plone_utils.addPortalMessage(_(u'News item changes saved.'))
return state.set(context=new_context)
