## Script (Python) "topic_editTopic"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=acquireCriteria, id=None, title=None, description=None
##title=
##
if not id:
    id = context.getId()
    
new_context = context.portal_factory.doCreate(context, id)
new_context.edit( acquireCriteria=acquireCriteria
                , title=title
                , description=description )
new_context.plone_utils.contentEdit( context
                                   , id=id
                                   , description=description)
return ( 'success'
       , new_context
       , { 'portal_status_message' : context.REQUEST.get( 'portal_status_message'
                                                        , 'Topic has been changed.')} )
