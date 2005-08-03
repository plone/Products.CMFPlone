from DateTime import DateTime
from Products.CMFCore.CMFCorePermissions import SetOwnPassword
from Products.CMFCore.utils import getToolByName, _checkPermission
from Products.CMFDefault.MembershipTool import MembershipTool as BaseTool
from Products.CMFPlone import ToolNames
from Products.CMFPlone.utils import _createObjectByType
from OFS.Image import Image
from AccessControl import ClassSecurityInfo, getSecurityManager
from Globals import InitializeClass, DTMLFile
from zExceptions import BadRequest
from AccessControl.SecurityManagement import noSecurityManager
from Acquisition import aq_base, aq_parent, aq_inner
from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

default_portrait = 'defaultUser.gif'

DEFAULT_MEMBER_CONTENT = """\
Default page for %s

  This is the default document created for you when
  you joined this community.

  To change the content just click the 'edit'
  tab above.
"""

_marker = object()

class MembershipTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.MembershipTool
    toolicon = 'skins/plone_images/user.gif'
    plone_tool = 1
    personal_id = '.personal'
    portrait_id = 'MyPortrait'
    default_portrait = 'defaultUser.gif'
    memberarea_type = 'Folder'
    security = ClassSecurityInfo()
    
    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )

    #XXX I'm not quite sure why getPortalRoles is declared 'Managed'
    #    in CMFCore.MembershipTool - but in Plone we are not so anal ;-)
    security.declareProtected(View, 'getPortalRoles')

    security.declareProtected(ManagePortal, 'manage_mapRoles')
    manage_mapRoles = DTMLFile('www/membershipRolemapping', globals())

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

    # XXX: Comment this out to see if we still need it.
    # We don't want to set wrapped users into the request!
    #def getAuthenticatedMember(self):
    #    """ """
    #    _user=self.REQUEST.get('_portaluser', None)
    #    if _user: # sanity check the cached user against the current user
    #        user_id = getSecurityManager().getUser().getId()
    #        if not user_id == _user.getId():
    #            _user = None
    #    if _user is None:
    #        _user = BaseTool.getAuthenticatedMember(self)
    #        self.REQUEST.set('_portaluser', _user)
    #    return _user
    
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
                       'location' : member.getProperty('location'),
                       'language' : member.getProperty('language'),
                       'home_page' : member.getProperty('home_page'),
                     }

        return memberinfo

    def getPersonalPortrait(self, member_id = None, verifyPermission=0):
        """
        returns the Portait for a member_id
        """
        membertool   = getToolByName(self, 'portal_memberdata')

        # what are we doing with that
        #if verifyPermission and not _checkPermission('View', portrait):
        #    return None
        if not member_id:
            member_id = self.getAuthenticatedMember().getUserName()

        portrait = membertool._getPortrait(member_id)
        if type(portrait) == type(''):
            portrait = None
        #portrait = None
        if portrait is None:
            portal = getToolByName(self, 'portal_url').getPortalObject()
            portrait = getattr(portal, default_portrait)

        return portrait

    def deletePersonalPortrait(self, member_id = None):
        """
        deletes the Portait of member_id
        """
        membertool   = getToolByName(self, 'portal_memberdata')

        if not member_id:
            member_id = self.getAuthenticatedMember().getUserName()

        membertool._deletePortrait(member_id)

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
        """
        if not member_id:
            member_id = self.getAuthenticatedMember().getUserName()

        if portrait and portrait.filename:
            portrait = Image(id=member_id, file=portrait, title='')
            membertool   = getToolByName(self, 'portal_memberdata')
            membertool._setPortrait(portrait, member_id)


##     security.declarePrivate('wrapUser')
##     def wrapUser(self, u):
##         self.createMemberarea(u.getId())
##         return BaseTool.wrapUser(self, u)

    def createMemberarea(self, member_id=None, minimal=1):
        """
        Create a member area for 'member_id' or the authenticated user.
        """
        if not self.getMemberareaCreationFlag():
            return None
        members = self.getMembersFolder()
        if members is None:
            return None
        if self.isAnonymousUser():
            return None
        catalog = getToolByName(self, 'portal_catalog')
        membership = getToolByName(self, 'portal_membership')

        if not member_id:
            # member_id is optional (see CMFCore.interfaces.portal_membership:
            #     Create a member area for 'member_id' or authenticated user.)
            member = membership.getAuthenticatedMember()
            member_id = member.getId()

        if hasattr(members, 'aq_explicit'):
            members=members.aq_explicit
        
        if hasattr(members, member_id):
            # has already this member
            # XXX exception
            return
        
        _createObjectByType(self.memberarea_type, members, id=member_id)

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

        ## translate the default content

        # get some translation interfaces

        translation_service = getToolByName(self, 'translation_service', _marker)
        if translation_service is _marker:
            # test environ, some other aberent sitch
            return
        
        utranslate = translation_service.utranslate
        encode = translation_service.encode
        
        # convert the member_id to unicode type
        umember_id = translation_service.asunicodetype(member_id, errors='replace')

        member_folder_title = utranslate(
            'plone', 'title_member_folder',
            {'member': umember_id}, self,
            default = "%s's Home" % umember_id)
       
        member_folder_description = utranslate(
            'plone', 'description_member_folder',
            {'member': umember_id}, self,
            default = 'Home page area that contains the items created ' \
            'and collected by %s' % umember_id)

        member_folder_index_html_title = utranslate(
            'plone', 'title_member_folder_index_html',
            {'member': umember_id}, self,
            default = "Home page for %s" % umember_id)
 
        # encode strings to site encoding as we dont like to store type unicode atm
        member_folder_title = encode(member_folder_title, errors='replace')
        member_folder_description = encode(member_folder_description, errors='replace')
        member_folder_index_html_title = encode(member_folder_index_html_title, errors='replace')

        ## Modify member folder
        member_folder = self.getHomeFolder(member_id)
        # Grant Ownership and Owner role to Member
        member_folder.changeOwnership(user)
        member_folder.__ac_local_roles__ = None
        member_folder.manage_setLocalRoles(member_id, ['Owner'])
        # XXX set title and description (edit invokes reindexObject)
        #member_folder.edit(title=member_folder_title,
        #                   description=member_folder_description)
        # We use ATCT now use the mutators
        member_folder.setTitle(member_folder_title)
        member_folder.setDescription(member_folder_description)
        member_folder.reindexObject()

        if not minimal:
            # if it's minimal, don't create the memberarea but do notification

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

    def listMembers(self):
        '''Gets the list of all members.
        THIS METHOD MIGHT BE VERY EXPENSIVE ON LARGE USER FOLDERS AND MUST BE USED
        WITH CARE! We plan to restrict its use in the future (ie. force large requests
        to use searchForMembers instead of listMembers, so that it will not be
        possible anymore to have a method returning several hundred of users :)
        '''
        uf = self.acl_users
        if hasattr(aq_base(uf), 'getPureUsers'): # GRUF
            return [BaseTool.wrapUser(self, x) for x in uf.getPureUsers()]
        else:
            return BaseTool.listMembers(self)

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
    #security.declarePublic( 'searchForMembers' )
    def searchForMembers( self, REQUEST=None, **kw ):
        """
        searchForMembers(self, REQUEST=None, **kw) => normal or fast search method.
        
        The following properties can be provided:
        - name
        - email
        - last_login_time
        - roles
        - groupname

        This is an 'AND' request.

        If name is provided, then a _fast_ search is performed with GRUF's
        searchUsersByName() method. This will improve performance.

        In any other case, a regular (possibly _slow_) search is performed.
        As it uses the listMembers() method, which is itself based on gruf.getUsers(),
        this can return partial results. This may change in the future.
        """
        md = self.portal_memberdata
        groups_tool = self.portal_groups
        if REQUEST:
            dict = REQUEST
        else:
            dict = kw

        name = dict.get('name', None)
        email = dict.get('email', None)
        roles = dict.get('roles', None)
        last_login_time = dict.get('last_login_time', None)
        before_specified_time = dict.get('before_specified_time', None)
        groupname = dict.get('groupname', '').strip()
        is_manager = self.checkPermission('Manage portal', self)

        if name:
            name = name.strip().lower()
        if not name:
            name = None
        if email:
            email = email.strip().lower()
        if not email:
            email = None

        # We want 'name' request to be handled properly with large user folders.
        # So we have to check both the fullname and loginname, without scanning all
        # possible users.
        md_users = None
        uf_users = None
        if name:
            # We first find in MemberDataTool users whose _full_ name match what we want.
            lst = md.searchMemberDataContents('fullname', name)
            md_users = [ x['username'] for x in lst]

            # Fast search management if the underlying acl_users support it.
            # This will allow us to retreive users by their _id_ (not name).
            acl_users = self.acl_users
            meth = getattr(acl_users, "searchUsersByName", None)
            if meth:
                uf_users = meth(name)           # gruf search

        # Now we have to merge both lists to get a nice users set.
        # This is possible only if both lists are filled (or we may miss users else).
        members = []
        g_userids, g_members = [], []
        
        if groupname:
            groups = groups_tool.searchForGroups(title=groupname) + \
                     groups_tool.searchForGroups(name=groupname)

            for group in groups:
                for member in group.getGroupMembers():
                    if member not in g_members and not groups_tool.isGroup(member):
                        g_members.append(member)
            g_userids = map(lambda x: x.getMemberId(), g_members)
        if groupname and not g_userids:
            return []

        if md_users is not None and uf_users is not None:
            names_checked = 1
            wrap = self.wrapUser
            getUser = acl_users.getUser
            for userid in md_users:
                if not g_userids or userid in g_userids:
                    members.append(wrap(getUser(userid)))
            for userid in uf_users:
                if userid in md_users:
                    continue             # Kill dupes
                if not g_userids or userid in g_userids:
                    members.append(wrap(getUser(userid)))

            # Optimization trick
            if not email and \
                   not roles and \
                   not last_login_time:
                return members
        elif groupname:
            members = g_members
            names_checked = 0
        else:
            # If the lists are not available, we just stupidly get the members list
            members = self.listMembers()
            names_checked = 0

        # Now perform individual checks on each user
        res = []
        portal = getToolByName(self, 'portal_url').getPortalObject()

        for member in members:
            #user = md.wrapUser(u)
            u = member.getUser()
            if not (member.getProperty('listed', None) or is_manager):
                continue
            if name and not names_checked:
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
                if type(member.getProperty('last_login_time','')) == type(''):
                    # value is a string when mem hasn't yet logged in
                    mem_last_login_time = DateTime(member.getProperty('last_login_time',None))
                else:
                    mem_last_login_time = member.last_login_time
                if before_specified_time:
                    if mem_last_login_time >= last_login_time:
                        continue
                elif mem_last_login_time < last_login_time:
                    continue
            res.append(member)
        return res

    def testCurrentPassword(self, password, username=None):
        """ test to see if password is current """
        portal=getToolByName(self, 'portal_url').getPortalObject()
        REQUEST=getattr(self, 'REQUEST', {})
        if username is None:
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
                raise BadRequest, 'did not find current user in any user folder'
            if registration:
                failMessage = registration.testPasswordValidity(password)
                if failMessage is not None:
                    raise BadRequest, failMessage

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
            raise BadRequest, 'Not logged in.'

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


    security.declareProtected(View, 'immediateLogout')
    def immediateLogout(self):
        """ Log the current user out immediately.  Used by logout.py so that
            we do not have to do a redirect to show the logged out status. """
        noSecurityManager()

MembershipTool.__doc__ = BaseTool.__doc__

InitializeClass(MembershipTool)
