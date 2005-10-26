## Script (Python) "publishItems"
##parameters=items=None, comment=''
##title=
##
wf_tool = context.portal_workflow

if items is None:

    items = []

    for obj in context.contentValues():

        if ( wf_tool.getInfoFor( obj, 'review_state', '' )
              in ( 'private', 'pending' ) ):
            items.append( obj.getId() )

for path in items:
    object = context.restrictedTraverse( path )
    wf_tool.doActionFor( object, 'publish', comment=comment )

context.REQUEST[ 'RESPONSE' ].redirect( '%s/review?%s'
                   % ( context.portal_url()
                     , 'portal_status_message=%d+items+published.'
                         % len( items )
                     ) )
