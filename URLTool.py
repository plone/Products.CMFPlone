from Products.CMFCore.URLTool import URLTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

from urlparse import urlparse

class URLTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.URLTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/link_icon.gif'

    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )

    security.declarePublic('isURLInPortal')
    def isURLInPortal(self, url):
        """ Check if a given url is on the same host and contains the portal
            path.  Used to ensure that login forms can determine relevant
            referrers (i.e. in portal).  Also return true for relative urls,
            though techincally they may not be part of the portal, it's a good
            guess (just like assuming https://portal is in the same portal as
            http://portal).
        """
        p_url = self()
        p_host_path = urlparse(p_url)[0:3]
        url_host_path = urlparse(url)[0:3]
        # check for urls without protocol (i.e. relative urls), or urls with
        # the same host and path.
        return (p_host_path[1] == url_host_path[1] and
          url_host_path[2].startswith(p_host_path[2])) or not url_host_path[0]

URLTool.__doc__ = BaseTool.__doc__

InitializeClass(URLTool)
