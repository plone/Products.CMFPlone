## Script (Python) "change_ownership"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userid, subobjects=0
##title=Change ownership
##

if subobjects:
    subobjects=1

context.plone_utils.changeOwnershipOf(context, userid, subobjects)

return context.portal_navigation.getNext( context
                                        , 'metadata_edit'
                                        , 'success'
                                        , portal_status_message='Ownership has been changed.' )

