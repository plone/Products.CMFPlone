from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.MembershipTool import MembershipTool as BaseTool
from Products.CMFDefault.MembershipTool import DEFAULT_MEMBER_CONTENT
from Products.CMFDefault.Document import addDocument

class MembershipTool( BaseTool ):
    """ Plone customized Membership Tool """
    meta_type='Plone Membership Tool'
    plone_tool = 1

    def createMemberarea(self, member_id):
        """
        since we arent using PortalFolders and invokeFactory will not work
        we must do all of this ourself. ;(
        """
        parent = self.aq_inner.aq_parent
        members =  getattr(parent, 'Members', None)
        if members is not None and not hasattr(members, member_id):
            f_title = "%s's Home" % member_id
            members.manage_addPloneFolder( id=member_id, title=f_title )
            f=getattr(members, member_id)
            # Grant ownership to Member
            acl_users = self.__getPUS()
            user = acl_users.getUser(member_id)
            if user is not None:
                user= user.__of__(acl_users)
            else:
                from AccessControl import getSecurityManager
                user= getSecurityManager().getUser()
                # check that we do not do something wrong
                if user.getUserName() != member_id:
                    raise NotImplementedError, \
                        'cannot get user for member area creation'
            f.changeOwnership(user)
            f.manage_setLocalRoles(member_id, ['Owner'])
            # Create Member's home page.
            # DEFAULT_MEMBER_CONTENT ought to be configurable per
            # instance of MembershipTool.
            addDocument( f
                       , 'index_html'
                       , member_id+"'s Home"
                       , member_id+"'s front page"
                       , "structured-text"
                       , (DEFAULT_MEMBER_CONTENT % member_id)
                       )
            f.index_html._setPortalTypeName( 'Document' )
            # Overcome an apparent catalog bug.
            f.index_html.reindexObject()
            wftool = getToolByName( f, 'portal_workflow' )
            wftool.notifyCreated( f.index_html )
            #XXX the above is copy/pasted from CMFDefault.MembershipTool only because
            #its not using invokeFactory('Folder') -- FIX IT!
            
            #XXX Below is what really is Plone customizations
            member_folder=self.getHomeFolder(member_id)
            member_folder.description = 'Home page area that contains the items created and ' \
                                        + 'collected by %s' % member_id
        
            member_folder.manage_addPloneFolder('.personal', 'Personal Items')
            personal=getattr(member_folder, '.personal')
            personal.description = "contains personal workarea items for %s" % member_id
            personal.changeOwnership(user)
            personal.manage_setLocalRoles(member_id, ['Owner'])
            
