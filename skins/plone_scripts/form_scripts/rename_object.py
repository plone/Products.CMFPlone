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
    id = REQUEST.get('id', '')
    id = REQUEST.get( 'field_id', id )

if id!=context.getId():
    try:
        context.manage_renameObjects( [context.getId()]
                                    , [id] 
                                    , REQUEST )
    except: #XXX have to do this for Topics and maybe other folderish objects
        context.aq_parent.manage_renameObjects( (context.getId(),), (id,), REQUEST)

    if redirect:
        status_msg=REQUEST.get( 'portal_status_message'
                              , 'Changes+have+been+Saved.')
        return REQUEST.RESPONSE.redirect('%s/%s?%s' % ( REQUEST['URL2']
                                                      , id
                                                      , 'portal_status_message=' + status_msg ) )
