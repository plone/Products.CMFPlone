## Script (Python) "rejectItems"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=items, comment=''
##title=
##
wf_tool = context.portal_workflow # XXX getToolByName
for path in items:
    object = context.restrictedTraverse( path )
    wf_tool.doActionFor( object, 'reject', comment=comment )

context.REQUEST[ 'RESPONSE' ].redirect( '%s/review?%s'
                   % ( context.portal_url()
                     , 'portal_status_message=Items+rejected.'
                     ) )
