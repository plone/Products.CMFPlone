from Products.CMFCore import MemberDataTool
from Products.CMFCore.MemberDataTool import MemberDataTool as BaseTool
from Products.CMFCore.MemberDataTool import MemberData as BaseData
from Products.CMFPlone import ToolNames
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

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

MemberDataTool.__doc__ = BaseTool.__doc__

InitializeClass(MemberDataTool)

class MemberData(BaseData):

    meta_type='Plone MemberData'

    def __init__(self):
        BaseData.__init__(self)

MemberData.__doc__ = BaseData.__doc__

InitializeClass(MemberData)
