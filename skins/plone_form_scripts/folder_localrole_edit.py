## Script (Python) "folder_localrole_edit"
##parameters=change_type
##title=Set local roles
##
pm = context.portal_membership

if change_type == 'add':
    pm.setLocalRoles( obj=context
                    , member_ids=context.REQUEST.get('member_ids', ())
                    , member_role=context.REQUEST.get('member_role', '')
                    )
else:
    pm.deleteLocalRoles( obj=context
                       , member_ids=context.REQUEST.get('member_ids', ())
                       )

qst='?portal_status_message=Local+Roles+changed.'

context.REQUEST.RESPONSE.redirect( context.absolute_url() + '/folder_localrole_form' + qst )
