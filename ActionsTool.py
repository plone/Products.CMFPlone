from Globals import InitializeClass, DTMLFile, package_home
from Products.CMFCore.ActionsTool import ActionsTool as BaseTool

class ActionsTool( BaseTool ):
    """
        Weave together the various sources of "actions" which are apropos
        to the current user and context.
    """

    id = 'portal_actions'
    meta_type = 'Plone Actions Tool'

InitializeClass(ActionsTool)
