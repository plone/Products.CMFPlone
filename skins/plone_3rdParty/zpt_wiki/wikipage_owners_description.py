## Script (Python) "wikipage_owners_description"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=owner
##title=
##
descriptions = { 'creator'        : 'Only creator of new page'
               , 'original_owner' : 'Only original page owner(s)'
               , 'both'           : 'Both original page owner(s)'
                                    ' and sub-page creators'
               }
return descriptions.get( owner, 'Unknown owner: %s' % owner )