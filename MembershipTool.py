from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission
from Products.CMFDefault.MembershipTool import MembershipTool as BaseTool
from Products.CMFPlone import ToolNames
from Products.CMFPlone.PloneUtilities import translate
from Products.CMFPlone.PloneUtilities import _createObjectByType
from OFS.Image import Image
from AccessControl import ClassSecurityInfo, getSecurityManager
from Globals import InitializeClass
from Acquisition import aq_base, aq_parent, aq_inner
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.CMFCorePermissions import SetOwnProperties
from Products.CMFCore.CMFCorePermissions import SetOwnPassword
from Products.CMFCore.CMFCorePermissions import View
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

default_portrait = 'defaultUser.gif'

DEFAULT_MEMBER_CONTENT = """\
Default page for %s

  This is the default document created for you when
  you joined this community.

  To change the content just click the 'edit'
  tab above.
"""

class MembershipTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.MembershipTool
    toolicon = 'skins/plone_images/user.gif'
    plone_tool = 1
    personal_id = '.personal'
    portrait_id = 'MyPortrait'
    default_portrait = 'defaultUser.gif'
    security = ClassSecurityInfo()
    
    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )

    #XXX I'm not quite sure why getPortalRoles is declared 'Managed'
    #    in CMFCore.MembershipTool - but in Plone we are not so anal ;-)
    security.declareProtected(View, 'getPortalRoles')

    security.declarePublic('getAuthenticatedMember')
    def getAuthenticatedMember(self):
        """ """
        _user=self.REQUEST.get('_portaluser', None)
        if _user: # sanity check the cached user against the current user
            user_id = getSecurityManager().getUser().getId()
            if not user_id == _user.getId():
                _user = None
        if _user is None:
            _user = BaseTool.getAuthenticatedMember(self)
            self.REQUEST.set('_portaluser', _user)
        return _user

    security.declarePublic('getPersonalPortrait')
    def getPersonalPortrait(self, member_id = None, verifyPermission=0):
        """
        returns the Portait for a member_id
        """
        membertool   = getToolByName(self, 'portal_memberdata')

        if not member_id:
            member_id = self.getAuthenticatedMember().getUserName()

        portrait = membertool._getPortrait(member_id)
        if type(portrait) == type(''):
            portrait = None
        if portrait is not None:
            if verifyPermission and not _checkPermission(View, portrait):
                # Don't return the portrait if the user can't get to it
                portrait = None
        if portrait is None:
            portal = getToolByName(self, 'portal_url').getPortalObject()
            portrait = getattr(portal, default_portrait)

        return portrait

    security.declareProtected(SetOwnProperties, 'deletePersonalPortrait')
    def deletePersonalPortrait(self, member_id = None):
        """
        deletes the Portait of member_id
        """
        membertool   = getToolByName(self, 'portal_memberdata')

        if not member_id:
            member_id = self.getAuthenticatedMember().getUserName()

        membertool._deletePortrait(member_id)

    security.declarePublic('getPersonalFolder')
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

    security.declareProtected(SetOwnProperties, 'changeMemberPortrait')
    def changeMemberPortrait(self, portrait, member_id=None):
        """
        given a portrait we will modify the users portrait
        we put this method here because we do not want
        .personal or portrait in the catalog
        """
        if not member_id:
            member_id = self.getAuthenticatedMember().getUserName()

        if portrait and portrait.filename:
            portrait = Image(id=member_id, file=portrait, title='')
            membertool   = getToolByName(self, 'portal_memberdata')
            membertool._setPortrait(portrait, member_id)

    security.declarePublic('createMemberarea')
    def createMemberarea(self, member_id=None, minimal=0):
        """
        Create a member area for 'member_id' or the authenticated user.
        """
        catalog = getToolByName(self, 'portal_catalog')
        membership = getToolByName(self, 'portal_membership')
        members = self.getMembersFolder()

        if not member_id:
            # member_id is optional (see CMFCore.interfaces.portal_membership:
            #     Create a member area for 'member_id' or authenticated user.)
            member = membership.getAuthenticatedMember()
            member_id = member.getId()

        if hasattr(members, 'aq_explicit'):
            members=members.aq_explicit

        if members is None:
            # no members area
            # XXX exception?
            return
        
        if hasattr(members, member_id):
            # has already this member
            # XXX exception
            return
        
        _createObjectByType('Folder', members, id=member_id)

        # get the user object from acl_users
        # XXX what about portal_membership.getAuthenticatedMember()?
        acl_users = self.__getPUS()
        user = acl_users.getUser(member_id)
        if user is not None:
            user= user.__of__(acl_users)
        else:
            user= getSecurityManager().getUser()
            # check that we do not do something wrong
            if user.getId() != member_id:
                raise NotImplementedError, \
                    'cannot get user for member area creation'

        ## get some translations
        member_folder_title = translate(
            'plone', 'title_member_folder',
            {'member': member_id}, self,
            default = "%s's Home" % member_id)
       
        member_folder_description = translate(
            'plone', 'description_member_folder',
            {'member': member_id}, self,
            default = 'Home page area that contains the items created ' \
            'and collected by %s' % member_id)

        member_folder_index_html_title = translate(
            'plone', 'title_member_folder_index_html',
            {'member': member_id}, self,
            default = "Home page for %s" % member_id)

        personal_folder_title = translate(
            'plone', 'title_member_personal_folder',
            {'member': member_id}, self,
            default = "Personal Items for %s" % member_id)

        personal_folder_description = translate(
            'plone', 'description_member_personal_folder',
            {'member': member_id}, self,
            default = 'contains personal workarea items for %s' % member_id)

        ## Modify member folder
        member_folder = self.getHomeFolder(member_id)
        # Grant Ownership and Owner role to Member
        member_folder.changeOwnership(user)
        member_folder.__ac_local_roles__ = None
        member_folder.manage_setLocalRoles(member_id, ['Owner'])
        # set title and description (edit invokes reindexObject)
        member_folder.edit(title=member_folder_title,
                           description=member_folder_description)
        member_folder.reindexObject()

        ## Create personal folder for personal items
        _createObjectByType('Folder', member_folder, id=self.personal_id)
        personal = getattr(member_folder, self.personal_id)
        personal.edit(title=personal_folder_title,
                      description=personal_folder_description)
        # Grant Ownership and Owner role to Member
        personal.changeOwnership(user)
        personal.__ac_local_roles__ = None
        personal.manage_setLocalRoles(member_id, ['Owner'])
        # Don't add .personal folders to catalog
        catalog.unindexObject(personal)
        
        if minimal:
            # don't set up the index_html for unit tests to speed up tests
            return

        ## add homepage text
        # get the text from portal_skins automagically
        homepageText = getattr(self, 'homePageText', None)
        if homepageText:
            member_object = self.getMemberById(member_id)
            portal = getToolByName(self, 'portal_url')
            # call the page template
            content = homepageText(member=member_object, portal=portal).strip()
            _createObjectByType('Document', member_folder, id='index_html')
            hpt = getattr(member_folder, 'index_html')
            # edit title, text and format
            # XXX
            hpt.setTitle(member_folder_index_html_title)
            if hpt.meta_type == 'Document':
                # CMFDefault Document
                hpt.edit(text_format='structured-text', text=content)
            else:
                hpt.update(text=content)
            hpt.setFormat('structured-text')
            hpt.reindexObject()
            # Grant Ownership and Owner role to Member
            hpt.changeOwnership(user)
            hpt.__ac_local_roles__ = None
            hpt.manage_setLocalRoles(member_id, ['Owner'])

        ## Hook to allow doing other things after memberarea creation.
        notify_script = getattr(member_folder, 'notifyMemberAreaCreated', None)
        if notify_script is not None:
            notify_script()

    # deal with ridiculous API change in CMF
    security.declarePublic('createMemberArea')
    createMemberArea = createMemberarea

    security.declareProtected(ManagePortal, 'listMembers')
    def listMembers(self):
        '''Gets the list of all members.
        '''
        uf = self.acl_users
        if hasattr(aq_base(uf), 'getPureUsers'): # GRUF
            return [BaseTool.wrapUser(self, x) for x in uf.getPureUsers()]
        else:
            return BaseTool.listMembers(self)

    security.declareProtected(ManagePortal, 'listMemberIds')
    def listMemberIds(self):
        '''Lists the ids of all members.  This may eventually be
        replaced with a set of methods for querying pieces of the
        list rather than the entire list at once.
        '''
        uf = self.acl_users
        if hasattr(aq_base(uf), 'getPureUserNames'): # GRUF
            return uf.getPureUserNames()
        else:
            return self.__getPUS().getUserNames()

    # this should probably be in MemberDataTool.py
    security.declarePublic('searchForMembers')
    def searchForMembers( self, REQUEST=None, **kw ):
        """ """
        if REQUEST:
            dict = REQUEST
        else:
            dict = kw

        name = dict.get('name', None)
        email = dict.get('email', None)
        roles = dict.get('roles', None)
        last_login_time = dict.get('last_login_time', None)
        is_manager = self.checkPermission('Manage portal', self)

        if name:
            name = name.strip().lower()
        if not name:
            name = None
        if email:
            email = email.strip().lower()
        if not email:
            email = None


        md = self.portal_memberdata

        res = []
        portal = self.portal_url.getPortalObject()

        for member in self.listMembers():
            #user = md.wrapUser(u)
            u = member.getUser()
            if not (member.listed or is_manager):
                continue
            if name:
                if (u.getUserName().lower().find(name) == -1 and
                    member.getProperty('fullname').lower().find(name) == -1):
                    continue
            if email:
                if member.getProperty('email').lower().find(email) == -1:
                    continue
            if roles:
                user_roles = member.getRoles()
                found = 0
                for r in roles:
                    if r in user_roles:
                        found = 1
                        break
                if not found:
                    continue
            if last_login_time:
                if member.last_login_time < last_login_time:
                    continue
            res.append(member)
        return res

    security.declareProtected(SetOwnPassword, 'testCurrentPassword')
    def testCurrentPassword(self, password):
        """ test to see if password is current """
        portal=getToolByName(self, 'portal_url').getPortalObject()
        REQUEST=getattr(self, 'REQUEST', {})
        username=self.getAuthenticatedMember().getUserName()
        acl_users = self._findUsersAclHome(username)
        if not acl_users:
            return 0
        return acl_users.authenticate(username, password, REQUEST)

    def _findUsersAclHome(self, userid):
        portal = getToolByName(self, 'portal_url').getPortalObject()
        acl_users=portal.acl_users
        parent = acl_users
        while parent:
            if acl_users.aq_explicit.getUserById(userid, None) is not None:
                break
            parent = aq_parent(aq_inner(parent)).aq_parent
            acl_users = getattr(parent, 'acl_users')
        if parent:
            return acl_users
        else:
            return None

    security.declareProtected(SetOwnPassword, 'setPassword')
    def setPassword(self, password, domains=None):
        '''Allows the authenticated member to set his/her own password.
        '''
        registration = getToolByName(self, 'portal_registration', None)
        if not self.isAnonymousUser():
            member = self.getAuthenticatedMember()
            acl_users = self._findUsersAclHome(member.getUserName())#self.acl_users
            if not acl_users:
                # should not possibly ever happen
                raise 'Bad Request', 'did not find current user in any user folder'
            if registration:
                failMessage = registration.testPasswordValidity(password)
                if failMessage is not None:
                    raise 'Bad Request', failMessage

            if domains is None:
                domains = []
            user = acl_users.getUserById(member.getUserName(), None)
            # we must change the users password trough grufs changepassword
            # to keep her  group settings
            if hasattr(user, 'changePassword'):
                user.changePassword(password)
            else:
                acl_users._doChangeUser(member.getUserName(), password, member.getRoles(), domains)
            self.credentialsChanged(password)
        else:
            raise 'Bad Request', 'Not logged in.'

MembershipTool.__doc__ = BaseTool.__doc__

InitializeClass(MembershipTool)
