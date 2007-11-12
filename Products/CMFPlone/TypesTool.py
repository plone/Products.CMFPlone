from Products.CMFCore.TypesTool import TypesTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

class TypesTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.TypesTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/document_icon.gif'

    security.declarePublic('listTypeTitles')
    def listTypeTitles(self, container=None):
        """ Return a dictionary of id/Title combinations """
        typenames = {}
        for t in self.listTypeInfo( container ):
            name = t.getId()
            if name:
                typenames[ name ] = t.title_or_id()

        return typenames

TypesTool.__doc__ = BaseTool.__doc__

InitializeClass(TypesTool)
