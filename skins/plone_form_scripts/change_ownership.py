## Script (Python) "change_ownership"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userid, subobjects=0
##title=Change ownership
##
from Products.CMFPlone import transaction_note

if subobjects:
    subobjects=1

context.plone_utils.changeOwnershipOf(context, userid, subobjects)
transaction_note('Changed owner of %s to %s' % (context.getId(), userid))

from Products.CMFPlone import transaction_note
transaction_note('Changed owner of %s at %s to %s' % (context.title_or_id(), context.absolute_url(), userid))

return context.portal_navigation.getNext( context
                                        , 'metadata_edit'
                                        , 'success'
                                        , portal_status_message='Ownership has been changed.' )
