from Products.CMFCore import MemberDataTool
from Products.CMFCore.MemberDataTool import MemberDataTool as BaseTool
from Products.CMFPlone import ToolNames
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFCore.permissions import ManagePortal

class MemberDataTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.MemberDataTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/user.gif'

    def __init__(self):
        BaseTool.__init__(self)
        self.portraits=BTreeFolder2(id='portraits')

    def _getPortrait(self, member_id):
        "return member_id's portrait if you can "
        return self.portraits.get(member_id, None)

    def _setPortrait(self, portrait, member_id):
        " store portrait which must be a raw image in _portrais "
        if self.portraits.has_key(member_id):
            self.portraits._delObject(member_id)
        self.portraits._setObject(id= member_id, object=portrait)

    def _deletePortrait(self, member_id):
        " remove member_id's portrait "
        if self.portraits.has_key(member_id):
            self.portraits._delObject(member_id)

    security.declarePrivate('pruneMemberDataContents')
    def pruneMemberDataContents(self):
        '''
        Compare the user IDs stored in the member data
        tool with the list in the actual underlying acl_users
        and delete anything not in acl_users
        '''
        BaseTool.pruneMemberDataContents(self)
        membertool= getToolByName(self, 'portal_membership')
        portraits   = self.portraits
        user_list = membertool.listMemberIds()

        for tuple in portraits.items():
            member_id = tuple[0]
            member_obj  = tuple[1]
            if member_id not in user_list:
                self.portraits._delObject(member_id)

    security.declareProtected(ManagePortal, 'purgeMemberDataContents')
    def purgeMemberDataContents(self):
        '''
        Delete ALL MemberData information. This is required for us as we change the
        MemberData class.
        '''
        membertool= getToolByName(self, 'portal_membership')
        members   = self._members

        for tuple in members.items():
            member_name = tuple[0]
            member_obj  = tuple[1]
            del members[member_name]

        return "Done."

    security.declarePrivate("updateMemberDataContents")
    def updateMemberDataContents(self,):
        """Update former MemberData objects to new MemberData objects
        """
        count = 0
        membertool= getToolByName(self, 'portal_membership')
        members   = self._members
        properties = self.propertyIds()

        # Scan members for old MemberData
        for member_name, member_obj in members.items():
            values = {}
            if getattr(member_obj, "_is_new_kind", None):
                continue        # Do not have to upgrade that object

            # Have to upgrade. Create the values mapping.
            for pty_name in properties:
                user_value = getattr( member_obj, pty_name, _marker )
                if user_value <> _marker:
                    values[pty_name] = user_value

            # Wrap a new user object of the RIGHT class
            u = self.acl_users.getUserById(member_name, None)
            if not u:
                continue                # User is not in main acl_users anymore
            self.wrapUser(u)

            # Set its properties
            mbr = self._members.get(member_name, None)
            if not mbr:
                raise RuntimeError, "Error while upgrading user '%s'." % (member_name, )
            mbr.setProperties(values, force_local = 1)
            count += 1

        return count


    security.declarePrivate( 'searchMemberDataContents' )
    def searchMemberDataContents( self, search_param, search_term ):
        """
        Search members.
        This is the same as CMFCore except that it doesn't check term case.
        """
        res = []

        search_term = search_term.strip().lower()

        if search_param == 'username':
            search_param = 'id'

        mtool   = getToolByName(self, 'portal_membership')

        for member_id in self._members.keys():

            user_wrapper = mtool.getMemberById( member_id )

            if user_wrapper is not None:
                memberProperty = user_wrapper.getProperty
                searched = memberProperty( search_param, None )

                if searched is not None:
                    if searched.strip().lower().find(search_term) != -1:

                        res.append( { 'username': memberProperty( 'id' )
                                      , 'email' : memberProperty( 'email', '' )
                                      }
                                    )
        return res

    security.declarePublic( 'searchFulltextForMembers' )
    def searchFulltextForMembers(self, s):
        """search for members which do have string 's' in name, email or full name (if defined)

        this is mainly used for the localrole form
        """

        s=s.strip().lower()

        portal = self.portal_url.getPortalObject()
        mu = self.portal_membership
        is_manager = mu.checkPermission('Manage portal', self)

        res = []
        for member in mu.listMembers():
            u = member.getUser()
            if not (member.listed or is_manager):
                continue
            if u.getUserName().lower().find(s) != -1 \
                or member.getProperty('fullname').lower().find(s) != -1 \
                or member.getProperty('email').lower().find(s) != -1:
                    res.append(member)
        return res

MemberDataTool.__doc__ = BaseTool.__doc__

InitializeClass(MemberDataTool)

_marker = []  # Create a new marker object.
