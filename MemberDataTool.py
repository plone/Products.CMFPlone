from Products.CMFCore import MemberDataTool
from Products.CMFCore.MemberDataTool import MemberDataTool as BaseTool
from Products.CMFCore.MemberDataTool import MemberData as BaseData
from Products.CMFCore.MemberDataTool import CleanupTemp
from Products.CMFPlone import ToolNames
from Globals import InitializeClass
from ZPublisher.Converters import type_converters
from zExceptions import BadRequest
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFCore.permissions import SetOwnProperties, ManagePortal
from ZODB.POSException import ConflictError


class MemberDataTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.MemberDataTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/user.gif'
    
    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )


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

##    security.declarePrivate('wrapUser')
##    def wrapUser(self, u):
##        '''
##        If possible, returns the Member object that corresponds
##        to the given User object.
##        We override this to ensure OUR MemberData class is used
##        '''
##        id = u.getId()
##        members = self._members
##        if not members.has_key(id):
##            # Get a temporary member that might be
##            # registered later via registerMemberData().
##            temps = self._v_temps
##            if temps is not None and temps.has_key(id):
##                m = temps[id]
##            else:
##                base = aq_base(self)
##                m = MemberData(base, id)
##                if temps is None:
##                    self._v_temps = {id:m}
##                    if hasattr(self, 'REQUEST'):
##                        # No REQUEST during tests.
##                        self.REQUEST._hold(CleanupTemp(self))
##                else:
##                    temps[id] = m
##        else:
##            m = members[id]
##        # Return a wrapper with self as containment and
##        # the user as context.
##        return m.__of__(self).__of__(u)

MemberDataTool.__doc__ = BaseTool.__doc__

InitializeClass(MemberDataTool)


_marker = []  # Create a new marker object.


class MemberData(BaseData):

    meta_type='Plone MemberData'
    security = ClassSecurityInfo()
    _is_new_kind = 1

    def __init__(self, *args, **kw):
        BaseData.__init__(self, *args, **kw)

    security.declareProtected(SetOwnProperties, 'setProperties')
    def setProperties(self, properties=None, **kw):
        '''Allows the authenticated member to set his/her own properties.
        Accepts either keyword arguments or a mapping for the "properties"
        argument.
        '''
        if properties is None:
            properties = kw
        membership = getToolByName(self, 'portal_membership')
        registration = getToolByName(self, 'portal_registration', None)
        if not membership.isAnonymousUser():
            member = membership.getAuthenticatedMember()
            if registration:
                failMessage = registration.testPropertiesValidity(properties, member)
                if failMessage is not None:
                    raise BadRequest, failMessage
            member.setMemberProperties(properties)
        else:
            raise BadRequest, 'Not logged in.'


    security.declarePublic('getProperty')
    def getProperty(self, id, default=_marker):
        tool = self.getTool()
        base = aq_base( self )

        # Check if we've got a marker asking us to get the value from the user object
        from_user = getattr(self, "%s_USER" % id, None)

        # First, check the wrapper (w/o acquisition).
        value = getattr( base, id, _marker )

        # Then, check the tool and the user object for a value.
        tool_value = tool.getProperty( id, _marker )
        user_value = getattr( self.getUser(), id, _marker )

        # New Plone behaviour: use user value if we've set it
        if from_user:
            if user_value is not _marker:
                return user_value

        # Return stored value if we've got one
        if value is not _marker:
            return value

        # If the tool doesn't have the property, use user_value or default
        if tool_value is _marker:
            if user_value is not _marker:
                return user_value
            elif default is not _marker:
                return default
            else:
                raise ValueError, 'The property %s does not exist' % id

        # If the tool has an empty property and we have a user_value, use it
        if not tool_value and user_value is not _marker:
            return user_value

        # Otherwise return the tool value
        return tool_value
        

    security.declarePrivate('setMemberProperties')
    def setMemberProperties(self, mapping, force_local = 0):
        '''Sets the properties of the member.
        If force_local is true, values will not be stored in the underlying user folder
        '''
        # Sets the properties given in the MemberDataTool.
        tool = self.getTool()
        for id in tool.propertyIds():
            if mapping.has_key(id):
                if not self.__class__.__dict__.has_key(id):
                    value = mapping[id]
                    if type(value)==type(''):
                        proptype = tool.getPropertyType(id) or 'string'
                        if type_converters.has_key(proptype):
                            value = type_converters[proptype](value)

                    # Try to update the property with GRUF's API
                    try:
                        if force_local:
                            raise RuntimeError, "Force storing in the MemberData object"
                            
                        # If it works, add a marker to retreive the data from the user object
                        self.setProperty(id, value)             # This is GRUF's method
                        setattr(self, "%s_USER" % id, 1)
                    except ConflictError:
                        raise
                    except:
                        # It didn't work... use the regular way, then - and remove the marker
                        setattr(self, id, value)
                        setattr(self, "%s_USER" % id, 0)        # Remove the marker
                    
        # Hopefully we can later make notifyModified() implicit.
        self.notifyModified()


MemberData.__doc__ = BaseData.__doc__

InitializeClass(MemberData)
