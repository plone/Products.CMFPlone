#script needs to migrate all folder objects to a Plone Folder and then get rid of the oroginal CMF folder
from __future__ import nested_scopes
from Products.CMFCore.utils import getToolByName

def log(msg):
    import sys
    sys.stdout.write( str(msg) +'\n')

def migrateFolders(self):
    root=getToolByName(self, 'portal_url').getPortalObject()
    old_folder='Folder'
    new_folder='Plone Folder'
    folder_types = ['Portal Folder', 'Plone Folder']

    def migrate(f):
	target=None
        if f.meta_type in (folder_types):
	   id, tmp_id = f.getId(), 'tmp__'+f.getId()
	   parent=f.aq_parent
	   if not hasattr(parent, 'portal_type'): 
               return
	   parent.invokeFactory(id=tmp_id, type_name='Folder')
	   src, target=getattr(parent, id), getattr(parent, tmp_id)
	   target.manage_pasteObjects( src.manage_copyObjects( src.objectIds()))
	   parent.manage_delObjects(id)
	   parent.manage_renameObjects( (tmp_id, ), (id, ) )
	for o in target.objectValues(folder_types):
            migrate(o)

    if getattr(self, 'meta_type', '')=='CMF Site':
        for f in self.objectValues(folder_types):
            migrate(f)
    else:
        for f in root.objectValues(folder_types):
            migrate(f)

    #take off syndication tab if its on Folder Type
    #folder_type = getToolByName(self, 'portal_types').getTypeInfo('Folder')
    #types_tool = getToolByName(self, 'portal_types')
    #actions = []
    #for idx in range( len(folder_type._actions)):
#	action=folder_type._actions[idx]
#        if action['id']!='syndication':
#            actions.append(action)
#    setattr( getattr(types_tool, 'Folder'), '_actions', actions)
    return 'finished migration'

