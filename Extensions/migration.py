# Clean Migration machinery 
# given a id of a portal in the container it will attempt to rename it
# and create a new instance of Plone and then migrate the old data to
# the new Plone..  this is really required for older Plone sites pre-1.0 
# coming of age.
from __future__ import nested_scopes
from Products.CMFCore.utils import getToolByName

def changeOwnershipOf(self, object, owner):
    """ changes the ownership of an object """
    membership=getToolByName(self, 'portal_membership')
    if owner not in membership.listMemberIds():
        raise KeyError, 'Only users in this site can be made owners.'
    acl_users=getattr(self, 'acl_users')
    user = acl_users.getUser(owner)
    if user is not None:
        user= user.__of__(acl_users)
    else:
        from AccessControl import getSecurityManager
        user= getSecurityManager().getUser()
    object.changeOwnership(user)

def change_ownershipIfNeeded(self, objs):
    url=getToolByName(self, 'portal_url')
    for o in objs:
        path=list(url.getRelativeContentPath(o))
        try:
            idx=path.index('Members')
            uname=path[idx+1]
            changeOwnershipOf(self, o, uname)
        except:
            pass

from ZODB.PersistentMapping import PersistentMapping
import copy
def copyZopeAttributes(old,new):
    #change the Ownership    
    try:
        changeOwnershipOf(old, new, old.getOwner().getId())
    except:
        pass
    if hasattr(new, '__acl_local_roles__'):
        new.__acl_local_roles__={}
        new.__acl_local_roles__.update(old.__acl_local_roles__)
    if hasattr(old, 'workflow_history'):
        new.workflow_history=PersistentMapping()
        new.workflow_history.__dict__=old.workflow_history.__dict__
    new.__dict__=old.__dict__        

def migrate_portal(self, id):
    """ migrates a Pre-1.0 Plone to Plone 1.0 compliance """
    folder_types = ['Portal Folder', 'Plone Folder']
    new_id='tmp_'+id
    self.manage_renameObjects( (id, ), (new_id, ) )
    original=getattr(self, new_id)
    self.manage_addProduct['CMFPlone'].manage_addSite( id=id
                                                     , title=original.title
                                                     , description=original.description
                                                     , create_userfolder=0
                                                     , email_from_address=original.email_from_address
                                                     , email_from_name=original.email_from_name
                                                     , validate_email=original.validate_email
                                                     , custom_policy='Default Plone' )    
    newsite=getattr(self, id)
    if 'acl_users' in original.objectIds():
        newsite.manage_pasteObjects( original.manage_copyObjects( ('acl_users',)))
    #portal_url.getRelativeContentPath(o)
    def do_migrate(o):

        if not hasattr(o,'portal_type'):
            return #its not content

        o_parent_path=o.portal_url.getRelativeContentPath(o.aq_parent)
        type_id=o.getTypeInfo().getId()
        new_parent=newsite.restrictedTraverse(o_parent_path)
        if not o.isPrincipiaFolderish:
            if o.getId() not in new_parent.objectIds():
                new_parent.invokeFactory(id=o.getId(), type_name=type_id)
                copyZopeAttributes(o, getattr(new_parent, o.getId()))
            return

        if o.getId() not in new_parent.objectIds():
            new_parent.invokeFactory(id=o.getId(), type_name=type_id)
        copyZopeAttributes(o, getattr(new_parent, o.getId()))
        for obj in o.objectValues():
            do_migrate(obj)
        return

    for f in original.objectValues(folder_types):
        do_migrate(f)

    return 'fin'
    
