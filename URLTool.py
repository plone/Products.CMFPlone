from Products.CMFCore.URLTool import URLTool as BaseTool

from Globals import InitializeClass

class URLTool(BaseTool):
    """ Plone URL Tool.
    """
    id = 'portal_url'
    meta_type = 'Plone URL Tool'

InitializeClass(URLTool)
