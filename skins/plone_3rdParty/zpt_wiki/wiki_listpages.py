## Script (Python) "wiki_listpages"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=sort_order=None
##title=
##
pages = context.objectValues( ['CMF Wiki Page'] )
if sort_order == 'modified':
    pages.sort( lambda x, y:
                    cmp( y.bobobase_modification_time()
                       , x.bobobase_modification_time()
                       ) )
else:
    pages.sort( lambda x, y:
                    cmp( x.getId(), y.getId() ) )

return pages