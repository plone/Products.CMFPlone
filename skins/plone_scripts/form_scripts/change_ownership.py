## Script (Python) "change_ownership"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userid
##title=Change ownership
##

context.plone_utils.changeOwnershipOf(context, userid)

return context.portal_navigation.getNext( context
                                        , 'metadata_edit'
                                        , 'success'
                                        , portal_status_message='Ownership has been changed.' )

