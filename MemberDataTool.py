from Products.CMFCore import MemberDataTool
from Products.CMFCore.MemberDataTool import MemberDataTool as BaseTool
from Products.CMFCore.MemberDataTool import MemberData as BaseData
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from BTrees.OOBTree import OOBTree
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2

class MemberDataTool(BaseTool):
    meta_type='Plone MemberData Tool'
    security=ClassSecurityInfo()

    def __init__(self):
        BaseTool.__init__(self)
        self.portraits=BTreeFolder2(id='portraits')

    def _getPortrait(self, member_id):
        "return member_id's portrait if you can "
        try:
            return self.portraits[member_id]
        except:
            pass

    def _setPortrait(self, portrait, member_id):
        " store portrait which must be a raw image in _portrais "
        try:
            self.portraits._delObject(member_id)
        except:
            pass
        self.portraits._setObject(id= member_id, object=portrait)

    security.declarePrivate('pruneMemberDataContents')
    def pruneMemberDataContents(self):
        '''
        Compare the user IDs stored in the member data
        tool with the list in the actual underlying acl_users
        and delete anything not in acl_users
        '''
        pruneMemberDataContents.pruneMemberDataContents(self)
        membertool= getToolByName(self, 'portal_membership')
        portraits   = self._portraits
        user_list = membertool.listMemberIds()

        for tuple in portraits.items():
            member_id = tuple[0]
            member_obj  = tuple[1]
            if member_name not in user_list:
                del _portraits[member_id]


InitializeClass(MemberDataTool)

class MemberData (BaseData):
    meta_type='Plone MemberData'
    def __init__(self):
        BaseData.__init__(self)
InitializeClass(MemberData)
