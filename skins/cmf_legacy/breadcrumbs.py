## Script (Python) "breadcrumbs.py $Revision: 1.3 $"
##parameters=include_root=1
##title=Return breadcrumbs
##
from string import join

result = []
portal_url = context.portal_url()

if include_root:
    result.append( { 'id'      : 'root'
                   , 'title'   : context.portal_properties.title()
                   , 'url'     : portal_url
                   }
                 )

relative = context.portal_url.getRelativeContentPath( context )
portal = context.portal_url.getPortalObject()

for i in range( len( relative ) ):
    now = relative[ :i+1 ]
    obj = portal.restrictedTraverse( now )
    if not now[ -1 ] == 'talkback':
        result.append( { 'id'      : now[ -1 ]
                       , 'title'   : obj.Title()
                       , 'url'     : portal_url + '/' + join( now, '/' )
                       }
                    )

return result
