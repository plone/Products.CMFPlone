from Products.CMFDefault.MembershipTool import MembershipTool as BaseTool

class MembershipTool( BaseTool ):
    """ Plone customized Membership Tool """
    meta_type='Plone Membership Tool'
    plone_tool = 1

    def createMemberarea(self, member_id):
        """
        provides some extra features
        """
        BaseTool.createMemberarea(self, member_id)
        member_folder=self.getHomeFolder(member_id)
        member_folder.setDescription('Home page area that contains the items created and collected by %s' % member_id)
        
        member_folder.invokeFactory(id='.personal', type_name='Folder')
        personal=getattr(member_folder, '.personal')
        personal.setTitle('Personal Items')
        personal.setDescription("contains personal workarea items for %s" % member_id)
