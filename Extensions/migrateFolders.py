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

    def migrate(f):
	log('inside migrate for ' + f.absolute_url() + '\n')
	log(f.isPrincipiaFolderish)
	target=None
        if f.isPrincipiaFolderish and f.meta_type!='Plone Folder':
	   id, tmp_id = f.getId(), 'tmp__'+f.getId()
	   parent=f.aq_parent
	   if not hasattr(parent, 'portal_type'): return
	   parent.invokeFactory(id=tmp_id, type_name=new_folder)
	   src,target=getattr(parent, f.getId()), getattr(parent, tmp_id)
	   target.manage_pasteObjects( src.manage_copyObjects( src.objectIds()))
	   parent.manage_delObjects(id)
	   parent.manage_renameObjects( (tmp_id, ), (id, ) )
	for o in target.objectValues('Portal Folder'):
	       migrate(o)
	       
    for f in root.objectValues('Portal Folder'):
        migrate(f)

    return 'finished migration'

