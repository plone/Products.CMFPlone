import PIL
from zope import event
from cStringIO import StringIO
from Products.CMFCore.utils import getToolByName, _checkPermission
from Products.CMFDefault.MembershipTool import MembershipTool as BaseTool
from Products.CMFPlone import ToolNames
from Products.CMFPlone.utils import scale_image
from OFS.Image import Image
from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import getSecurityManager
from Globals import InitializeClass, DTMLFile
from zExceptions import BadRequest
from ZODB.POSException import ConflictError
from AccessControl.SecurityManagement import noSecurityManager
from Acquisition import aq_base, aq_parent, aq_inner
from Products.PlonePAS.events import UserLoggedInEvent
from Products.PlonePAS.events import UserInitialLoginInEvent
from Products.PlonePAS.events import UserLoggedOutEvent
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.permissions import ManageUsers
from Products.CMFCore.permissions import SetOwnProperties
from Products.CMFCore.permissions import SetOwnPassword
from Products.CMFCore.permissions import View
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from AccessControl.requestmethod import postonly

default_portrait = 'defaultUser.gif'

class MembershipTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.MembershipTool
    toolicon = 'skins/plone_images/user.gif'
    plone_tool = 1
    personal_id = '.personal'
    portrait_id = 'MyPortrait'
    default_portrait = 'defaultUser.gif'
    memberarea_type = 'Folder'
    security = ClassSecurityInfo()

    manage_options = (BaseTool.manage_options +
                      ( { 'label' : 'Portraits'
                     , 'action' : 'manage_portrait_fix'
                     },))

    # TODO I'm not quite sure why getPortalRoles is declared 'Managed'
    #    in CMFCore.MembershipTool - but in Plone we are not so anal ;-)
    security.declareProtected(View, 'getPortalRoles')

    security.declareProtected(ManagePortal, 'manage_mapRoles')
    manage_mapRoles = DTMLFile('www/membershipRolemapping', globals())

    security.declareProtected(ManagePortal, 'manage_portrait_fix')
    manage_portrait_fix = DTMLFile('www/portrait_fix', globals())

    security.declareProtected(ManagePortal, 'manage_setMemberAreaType')
    def manage_setMemberAreaType(self, type_name, REQUEST=None):
        """ ZMI method to set the home folder type by its type name.
        """
        self.setMemberAreaType(type_name)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()
                    + '/manage_mapRoles'
                    + '?manage_tabs_message=Member+area+type+changed.')

    security.declareProtected(ManagePortal, 'setMemberAreaType')
    def setMemberAreaType(self, type_name):
        """ Sets the portal type to use for new home folders.
        """
        # No check for folderish since someone somewhere may actually want
        # members to have objects instead of folders as home "directory".
        self.memberarea_type = str(type_name).strip()

    security.declarePublic('getMemberInfo')
    def getMemberInfo(self, memberId=None):
        """
        Return 'harmless' Memberinfo of any member, such as Full name,
        Location, etc
        """
        if not memberId:
            member = self.getAuthenticatedMember()
        else:
            member = self.getMemberById(memberId)

        if member is None:
            return None

        memberinfo = { 'fullname'    : member.getProperty('fullname'),
                       'description' : member.getProperty('description'),
                       'location'    : member.getProperty('location'),
                       'language'    : member.getProperty('language'),
                       'home_page'   : member.getProperty('home_page'),
                       'username'    : member.getUserName(),
                     }

        return memberinfo

    security.declarePublic('getPersonalPortrait')
    def getPersonalPortrait(self, member_id = None, verifyPermission=0):
        """
        returns the Portrait for a member_id
        """
        membertool   = getToolByName(self, 'portal_memberdata')

        if not member_id:
            member_id = self.getAuthenticatedMember().getId()

        portrait = membertool._getPortrait(member_id)
        if type(portrait) == type(''):
            portrait = None
        if portrait is not None:
            if verifyPermission and not _checkPermission('View', portrait):
                # Don't return the portrait if the user can't get to it
                portrait = None
        if portrait is None:
            portal = getToolByName(self, 'portal_url').getPortalObject()
            portrait = getattr(portal, default_portrait)

        return portrait

    security.declareProtected(SetOwnProperties, 'deletePersonalPortrait') 
    def deletePersonalPortrait(self, member_id = None):
        """
        deletes the Portrait of member_id
        """
        membertool   = getToolByName(self, 'portal_memberdata')

        if not member_id:
            member_id = self.getAuthenticatedMember().getId()

        membertool._deletePortrait(member_id)

    security.declarePublic('getHomeFolder')
    def getHomeFolder(self, id=None, verifyPermission=0):
        """ Return a member's home folder object, or None.
        dwm: straight from CMF1.5.2
        """
        if id is None:
            member = self.getAuthenticatedMember()
            if not hasattr(member, 'getMemberId'):
                return None
            id = member.getMemberId()
        members = self.getMembersFolder()
        if members:
            try:
                folder = members._getOb(id)
                if verifyPermission and not _checkPermission(View, folder):
                    # Don't return the folder if the user can't get to it.
                    return None
                return folder
            # KeyError added to deal with btree member folders
            except (AttributeError, KeyError, TypeError):
                pass
        return None

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
            member_id = self.getAuthenticatedMember().getId()

        if portrait and portrait.filename:
            scaled, mimetype = scale_image(portrait)
            portrait = Image(id=member_id, file=scaled, title='')
            membertool   = getToolByName(self, 'portal_memberdata')
            membertool._setPortrait(portrait, member_id)

    security.declareProtected(ManageUsers, 'listMembers')
    def listMembers(self):
        '''Gets the list of all members.
        THIS METHOD MIGHT BE VERY EXPENSIVE ON LARGE USER FOLDERS AND MUST BE USED
        WITH CARE! We plan to restrict its use in the future (ie. force large requests
        to use searchForMembers instead of listMembers, so that it will not be
        possible anymore to have a method returning several hundred of users :)
        '''
        uf = self.acl_users
        if uf.meta_type == 'Group User Folder':
            return [BaseTool.wrapUser(self, x) for x in uf.getPureUsers()]
        else:
            return BaseTool.listMembers(self)

    security.declareProtected(ManageUsers, 'listMemberIds')
    def listMemberIds(self):
        '''Lists the ids of all members.  This may eventually be
        replaced with a set of methods for querying pieces of the
        list rather than the entire list at once.
        '''
        uf = self.acl_users
        if hasattr(aq_base(uf), 'getPureUserIds'): # GRUF
            return uf.getPureUserIds()
        else:
            return self.__getPUS().getUserIds()

    security.declareProtected(SetOwnPassword, 'testCurrentPassword')
    def testCurrentPassword(self, password):
        """ test to see if password is current """
        REQUEST=getattr(self, 'REQUEST', {})
        userid=self.getAuthenticatedMember().getUserId()
        acl_users = self._findUsersAclHome(userid)
        if not acl_users:
            return 0
        return acl_users.authenticate(userid, password, REQUEST)

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
    def setPassword(self, password, domains=None, REQUEST=None):
        '''Allows the authenticated member to set his/her own password.
        '''
        registration = getToolByName(self, 'portal_registration', None)
        if not self.isAnonymousUser():
            member = self.getAuthenticatedMember()
            acl_users = self._findUsersAclHome(member.getUserId())#self.acl_users
            if not acl_users:
                # should not possibly ever happen
                raise BadRequest, 'did not find current user in any user folder'
            if registration:
                failMessage = registration.testPasswordValidity(password)
                if failMessage is not None:
                    raise BadRequest, failMessage

            if domains is None:
                domains = []
            user = acl_users.getUserById(member.getUserId(), None)
            # we must change the users password trough grufs changepassword
            # to keep her  group settings
            if hasattr(user, 'changePassword'):
                user.changePassword(password)
            else:
                acl_users._doChangeUser(member.getUserId(), password, member.getRoles(), domains)
            self.credentialsChanged(password, REQUEST=REQUEST)
        else:
            raise BadRequest, 'Not logged in.'
    setPassword = postonly(setPassword)

    security.declareProtected(View, 'getCandidateLocalRoles')
    def getCandidateLocalRoles(self, obj):
        """ What local roles can I assign?
            Override the CMFCore version so that we can see the local roles on
            an object, and so that local managers can assign all roles locally.
        """
        member = self.getAuthenticatedMember()
        # Use getRolesInContext as someone may be a local manager
        if 'Manager' in member.getRolesInContext(obj):
            # Use valid_roles as we may want roles defined only on a subobject
            local_roles = [r for r in obj.valid_roles() if r not in
                            ('Anonymous', 'Authenticated', 'Shared')]
        else:
            local_roles = [ role for role in member.getRolesInContext(obj)
                            if role not in ('Member', 'Authenticated') ]
        local_roles.sort()
        return tuple(local_roles)


    security.declareProtected(View, 'loginUser')
    def loginUser(self, REQUEST=None):
        """ Handle a login for the current user.

        This method takes care of all the standard work that needs to be
        done when a user logs in:
        - clear the copy/cut/paste clipboard
        - PAS credentials update
        - sending a logged-in event
        - storing the login time
        - create the member area if it does not exist
        """
        user=getSecurityManager().getUser()
        if user is None:
            return

        if self.setLoginTimes():
            event.notify(UserInitialLoginInEvent(user))
        else:
            event.notify(UserLoggedInEvent(user))

        if REQUEST is None:
            REQUEST=getattr(self, 'REQUEST', None)
        if REQUEST is None:
            return

        # Expire the clipboard
        if REQUEST.get('__cp', None) is not None:
            REQUEST.RESPONSE.expireCookie('__cp', path='/')

        self.createMemberArea()

        try:
            pas = getToolByName(self, 'acl_users')
            pas.credentials_cookie_auth.login()
        except AttributeError:
            # The cookie plugin may not be present
            pass


    security.declareProtected(View, 'logoutUser')
    def logoutUser(self, REQUEST=None):
        """Process a user logout.

        This takes care of all the standard logout work:
        - ask the user folder to logout
        - expire a skin selection cookie
        - invalidate a Zope session if there is one
        """
        # Invalidate existing sessions, but only if they exist.
        sdm = getToolByName(self, 'session_data_manager', None)
        if sdm is not None:
                session = sdm.getSessionData(create=0)
                if session is not None:
                            session.invalidate()

        if REQUEST is None:
            REQUEST=getattr(self, 'REQUEST', None)
        if REQUEST is not None:
            pas = getToolByName(self, 'acl_users')
            try:
                pas.logout(REQUEST)
            except:
                # XXX Bare except copied from logout.cpy. This should be
                # changed in the next Plone release.
                pass

            # Expire the skin cookie if it is not configured to persist
            st = getToolByName(self, "portal_skins")
            skinvar = st.getRequestVarname()
            if REQUEST.has_key(skinvar) and not st.getCookiePersistence():
                    portal = getToolByName(self, "portal_url").getPortalObject()
                    path = '/' + portal.absolute_url(1)
                    # XXX check if this path is sane
                    REQUEST.RESPONSE.expireCookie(skinvar, path=path)

        user=getSecurityManager().getUser()
        if user is not None:
            event.notify(UserLoggedOutEvent(user))

    security.declareProtected(View, 'immediateLogout')
    def immediateLogout(self):
        """ Log the current user out immediately.  Used by logout.py so that
            we do not have to do a redirect to show the logged out status. """
        noSecurityManager()

    security.declarePublic('setLoginTimes')
    def setLoginTimes(self):
        """ Called by logged_in to set the login time properties
            even if members lack the "Set own properties" permission.

            The return value indicates if this is the first logged
            login time.
        """
        res=False
        if not self.isAnonymousUser():
            member = self.getAuthenticatedMember()
            login_time = member.getProperty('login_time', '2000/01/01')
            if str(login_time) == '2000/01/01':
                res=True
                login_time = self.ZopeTime()
            member.setProperties(login_time=self.ZopeTime(),
                                 last_login_time=login_time)
        return res

    security.declareProtected(ManagePortal, 'getBadMembers')
    def getBadMembers(self):
        """Will search for members with bad images in the portal_memberdata
        delete their portraits and return their member ids"""
        memberdata = getToolByName(self, 'portal_memberdata')
        portraits = getattr(memberdata, 'portraits', None)
        if portraits is None:
            return []
        bad_member_ids = []
        import transaction
        TXN_THRESHOLD = 50
        counter = 1
        for member_id in tuple(portraits.objectIds()):
            portrait = portraits[member_id]
            portrait_data = str(portrait.data)
            if portrait_data == '':
                continue
            try:
                img = PIL.Image.open(StringIO(portrait_data))
            except ConflictError:
                pass
            except:
                # Anything else we have a bad bad image and we destroy it
                # and ask questions later.
                portraits._delObject(member_id)
                bad_member_ids.append(member_id)
            if not counter%TXN_THRESHOLD:
                transaction.savepoint(optimistic=True)
            counter = counter + 1

        return bad_member_ids

MembershipTool.__doc__ = BaseTool.__doc__

InitializeClass(MembershipTool)
