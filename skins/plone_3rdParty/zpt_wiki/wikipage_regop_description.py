## Script (Python) "wikipage_regop_description"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=op
##title=
##
descriptions = { 'create'  : 'Create new pages from this one.'
               , 'edit'    : 'Change the text.'
               , 'comment' : 'Append text to end.'
               , 'move'    : 'Rename, delete, reparent.'
               }
return descriptions.get( op, 'Unknown operation: %s' % op )