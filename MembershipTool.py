from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.MembershipTool import MembershipTool as BaseTool
from Products.CMFDefault.Document import addDocument
from Acquisition import aq_base

default_portrait = 'defaultUser.gif'

DEFAULT_MEMBER_CONTENT = """\
Default page for %s

  This is the default document created for you when
  you joined this community.

  To change the content just click the 'edit'
  tab above.
"""
        
class MembershipTool( BaseTool ):
    """ Plone customized Membership Tool """
    meta_type='Plone Membership Tool'
    plone_tool = 1
    personal_id = '.personal'
    portrait_id = 'MyPortrait'
    default_portrait = 'defaultUser.gif'
    
    def getPersonalPortrait(self, member_id=None):
        """
        returns the Portait for a member_id
        """
        portrait=None
        personal=self.getPersonalFolder(member_id)

        if personal:
            portrait=getattr( personal
                            , self.portrait_id
                            , None )

        if portrait is None:
            portal = getToolByName(self, 'portal_url').getPortalObject()
            portrait = getattr(portal, default_portrait)

        return portrait

    def getPersonalFolder(self, member_id=None):
        """
        returns the Personal Item folder for a member
        if no Personal Folder exists will return None
        """
        home=self.getHomeFolder(member_id)
        personal=None
        if home:
            personal=getattr( home
                            , self.personal_id
                            , None )
        return personal

    def changeMemberPortrait(self, portrait, member_id=None):
        """ 
        given a portrait we will modify the users portrait
        we put this method here because we do not want
        .personal or portrait in the catalog

        portraits are $MemberHomeFolder/.personal/MyPortrait
        """
        if portrait and portrait.filename:
            catalog=getToolByName(self, 'portal_catalog')
            personal=self.getPersonalFolder(member_id)
            if not personal:
                home=self.getHomeFolder(member_id)
                home.invokeFactory(id=self.personal_id, type_name='Folder')
                personal=getattr(home, self.personal_id)
                catalog.unindexObject(personal) #remove persona folder from catalog
            if hasattr(personal, self.portrait_id):
                personal.manage_delObjects(self.portrait_id)
            personal.invokeFactory(id=self.portrait_id, type_name='Image')
            portrait_obj=getattr(personal, self.portrait_id, None)
            portrait_obj.edit(file=portrait)
            catalog.unindexObject(portrait_obj) #remove portrait image from catalog
                
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
            # go get the home page text from the skin
            DEFAULT_MEMBER_CONTENT = self.homePageText()

            addDocument( f
                       , 'index_html'
                       , member_id+"'s Home Page"
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
            
            catalog = getToolByName(self, 'portal_catalog')
            catalog.unindexObject(personal) #dont add .personal folders to catalog
