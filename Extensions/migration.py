# WARNING: Deprecated
# This script is to update old Plone sites before the release of beta 3 only
# With beta 3 we added a migration tool that does most of this work, you
# may use this for migrating alpha releases, but it is no longer supported
# and may not work.
#
# Please see http://plone.org/documentation/book/2 for more information
# on migration
#
# PROCEED AT YOUR OWN RISK
#
# Clean Migration machinery 
# given a id of a portal in the container it will attempt to rename it
# and create a new instance of Plone and then migrate the old data to
# the new Plone..  this is really required for older Plone sites pre-1.0 
# coming of age.
#
# WARNING:
# back up var/Data.fs before you attempt to run the migration machinery
# it has not been well tested and could have unexpected consequences
# Usage:
# create an external method in the folder where your CMF/Plone sites
# id: migrate_folders
# module: CMFPlone.migration
# function: migrate_folder
#
# now create a Python Script called gogo_migrate it should be simple
# return context.migrate_folder('source_portalobject_id','dest_portalobject_id')
#
#------snip----
# Modified by Sigve Tjora
# Correctly migrates subfolders
# Copies none portal content to new site
# Returns verbose output where you can check how the different parts were migrated
# Added possibility to migrate from old folder to new folder that already is created 
# Uses cruel approach to migrate folder content. First deletes all objects, then copies
# them over again. This is to make sure migration is performed on all objects. Should be
# done better, but that requires more knowledge of Zope-internals than I have.
#
# To use:
# - Make a new plone-site without acl_users.
# - Copy workflow and configure workflowtool to use same workflow as old site. It might
#   work without this step, but it is not tested.
# - Install all the types you are going to migrate in portal_type of your new portal.
#   E.g. install CMFPhoto, CMFImageDoc and other custom types that your old site uses.
#   If the script can't find the right type-information, the object is not migrated or copied, just discarded!
# - Run the migrate_folder("source_folder_id", "dest_folder_id") function via a python_script.
#   Both folders must be in the same folder in this version. The script must be run from this folder.
#
# You might have to edit the migration.py file to include more portal_tools to be ignored,
# but it should work without it. If a object with the same id as the one that is being
# migrated is found in the destination folder, then the object is not migrated.
# I have used a modified version of this script to migrate a production site from
# CMF beta 1.1 to Plone cvs head (after Alpha 4).
# I hope this is useful for someone!
#---------TODO------------
# portal_metadata elements should be migrated
# portal_catalog indexes/metadata should be migrated
# custom actions on all the tools should be migrated (action providers should be checked)
# Plone Folders local roles and security settings should be migrated
# portal_skins - custom skin folders that are ZODB based
# come up w/ migration document.. should be in sync w/ developers document
# !! How to write content that conforms with plone migration machinery !!


from __future__ import nested_scopes
from Products.CMFCore.utils import getToolByName
from cStringIO import StringIO
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from ZODB.PersistentMapping import PersistentMapping

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
    ret=''
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
        ret=ret+"Copied workflow_history\n"
    else:
        ret=ret+'Didnt have workflow_history: '+new.getId()+'\n'
    new.__dict__.update(old.__dict__)
    ret=ret+"Delete object(s): "+repr(new.objectIds())+"\n"
    new.manage_delObjects(new.objectIds())

    #I used this to make sure manager could modify all content.
    #It was necisary because of the workflow I used on the old site
    try:
        new.manage_permission(ModifyPortalContent, ['Manager'], 1)
    except:
        ret=ret+'Couldnt change permission: '+new.getId()+'\n'
    return ret

def migrate_portal(self, id):
    """ migrates a Pre-1.0 Plone to Plone 1.0 compliance """
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
    return migrate_folder(self, new_id, id)

def migrate_folder(self, source_folder_id, dest_folder_id):
    """Migrates a folder (e.g. CMF site) to a new folder that allready is created
    """

    out=StringIO() #outputstring
    folder_types = ['Portal Folder', 'Plone Folder']    
    portal_tools= ['portal_actions', 'portal_catalog'
                   ,'portal_discussion', 'portal_membership', 'portal_metadata', 'portal_navigation', 'portal_properties',
                   'portal_registration','portal_skins','portal_syndication','portal_types','portal_undo','portal_url','portal_workflow']
    original=getattr(self, source_folder_id)
    newsite=getattr(self, dest_folder_id)
    new_typetool=newsite.portal_types

    def do_migrate(o):
        out.write("\nMigrating object: "+o.getId()+"\n")
        if o.getId() in portal_tools:
            out.write("Didn't migrate tool: "+o.getId()+'\n')
            return #don't migrate tools...
        try:
            o_parent_path=o.portal_url.getRelativeContentPath(o.aq_parent)
        except:
            out.write("couldn't find relativeContentPath for "+o.getId()+'\n')
            return
        try:
            type_id=o.getTypeInfo().getId()
        except:
            out.write('Error getting typeinfo for '+o.getId()+'\n')
            return
        new_parent=newsite.restrictedTraverse(o_parent_path)
        if not hasattr(o.aq_base,'portal_type'):
            if o.getId() not in new_parent.objectIds():
                out.write('Raw copy of: '+o.getId()+'\n')
                try:
                    new_parent.manage_pasteObjects( o.aq_parent.manage_copyObjects( (o.getId(),)))
                except:
                    out.write('Raw copy didnt work')
                    
                new_object=None
                try:
                    new_object=new_parent[o.getId()]
                    owner_id=o.getOwner().getUserName()
                    user=newsite.acl_users.getUser(owner_id).__of__(newsite.acl_users)
                    new_object.changeOwnership(user)
                except:
                    out.write('Problems transfering Membership')
                try:
                    wf_history=PersistentMapping()
                    wf_history.update(o.workflow_history.__dict__)
                    new_object.workflow_history=wf_history
                except:
                    out.write( o.absolute_url()  + ' worklfow history could not be xfered ' )
            else:
                out.write('Object existed :'+o.getId()+'\n')
            return #its not content, just copied. Content in other folders will not be migrated.

        o_parent_path=o.portal_url.getRelativeContentPath(o.aq_parent)
        type_id=o.getTypeInfo().getId()
        new_parent=newsite.restrictedTraverse(o_parent_path)

        if not type_id in new_typetool.listContentTypes(new_parent):
            out.write("Object "+new_parent.getId()+" couldn't contain "+o.getId()+" of type "+type_id+"\n")
            return
        
        if not o.isPrincipiaFolderish:
            if o.getId() not in new_parent.objectIds():
                new_parent.invokeFactory(id=o.getId(), type_name=type_id)
            else:
                out.write( "Object was already there:" + o.getId()+"\n")
            out.write(copyZopeAttributes(o, getattr(new_parent, o.getId())))
            return

        if o.getId() not in new_parent.objectIds():
            new_parent.invokeFactory(id=o.getId(), type_name=type_id)
            out.write( "We are migrating portal folder:" + o.getId()+"\n")
        else:
            out.write( "Folder was already there:" + o.getId()+"\n")
            
        out.write(copyZopeAttributes(o, getattr(new_parent, o.getId())))
        for obj in o.objectValues():
            do_migrate(obj)
        return

    newsite.manage_pasteObjects( original.manage_copyObjects('acl_users') ) #copy over acl_users so we can xfer Ownership
    
    memberdata_properties=newsite.portal_memberdata.propertyIds()
    for memberid in newsite.portal_membership.listMemberIds():
        newmember=newsite.portal_membership.getMemberById(memberid)
        oldmember=original.portal_membership.getMemberById(memberid)
        properties={}

        for property in memberdata_properties:
            properties.update( {property:getattr(oldmember,property,'')} ) 
        try:
            newmember.setMemberProperties( properties )
        except:
            out.write( newmember.getUserName() + ' could not migrate users memberdata \n' )

    out.write("successfully set new portal_memberdata properties manually\n") #XXX should be done using BTree.copy()

    for f in original.objectValues():
        if original.getId() not in ('acl_users', ):
            do_migrate(f)
    newsite.portal_catalog.refreshCatalog(clear=1)    
    out.write("Finished"+'\n')
    return out.getvalue()
    
