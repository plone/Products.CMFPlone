from Globals import InitializeClass
from Products.CMFCore.TypesTool import TypesTool as BaseTool

class TypesTool( BaseTool ):
    """
        Provides a configurable registry of portal content types.
    """

    id = 'portal_types'
    meta_type = 'Plone Types Tool'

InitializeClass( TypesTool )
