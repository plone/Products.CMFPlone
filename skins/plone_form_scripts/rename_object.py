## Script (Python) "rename_object"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=redirect=1,id=''
##title=
##

REQUEST=context.REQUEST
if not id:
    id = REQUEST.get( 'field_id'
                    , REQUEST.get( 'id'
	                         , '') )
if id!=context.getId():
    context.manage_renameObjects( [context.getId()]
                                , [id]
				, REQUEST )
    if redirect:
        status_msg=REQUEST.get( 'portal_status_message'
	                      , 'Changes+have+been+Saved.')
        return REQUEST.RESPONSE.redirect('%s/%s?%s' % ( REQUEST['URL2']
                                                      , id
                                                      , 'portal_status_message=' + status_msg ) )
