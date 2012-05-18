from Products.CMFCore.URLTool import URLTool as BaseTool
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

from posixpath import normpath
from urlparse import urlparse, urljoin


class URLTool(PloneBaseTool, BaseTool):

    meta_type = 'Plone URL Tool'
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/link_icon.png'

    security.declarePublic('isURLInPortal')
    def isURLInPortal(self, url, context=None):
        """ Check if a given url is on the same host and contains the portal
            path.  Used to ensure that login forms can determine relevant
            referrers (i.e. in portal).  Also return true for some relative urls
            if context is passed in to allow for url parsing. When context is
            not provided, assume that relative urls are in the portal. It is
            assumed that http://portal is the same portal as https://portal.

            External sites listed in 'allow_external_login_sites' of
            site_properties are also considered within the portal to allow for
            single sign on.
        """
        p_url = self()

        _, u_host, u_path, _, _, _ = urlparse(url)
        if not u_host and not u_path.startswith('/'):
            if context is None:
                return True #old behavior
            if not context.isPrincipiaFolderish:
                useurl = context.aq_parent.absolute_url()
            else:
                useurl = context.absolute_url()
        else:
            useurl = p_url # when u_path.startswith('/')
        if not useurl.endswith('/'):
            useurl += '/'

        # urljoin to current url to get an absolute path
        _, u_host, u_path, _, _, _ = urlparse(urljoin(useurl, url))

        # normalise to end with a '/' so /foobar is not considered within /foo
        if not u_path:
            u_path = '/'
        else:
            u_path = normpath(u_path)
            if not u_path.endswith('/'):
                u_path += '/'
        _, host, path, _, _, _ = urlparse(p_url)
        if not path.endswith('/'):
            path += '/'
        if host == u_host and u_path.startswith(path):
            return True

        props = getToolByName(self, 'portal_properties').site_properties
        for external_site in props.getProperty('allow_external_login_sites', []):
            _, host, path, _, _, _ = urlparse(external_site)
            if not path.endswith('/'):
                path += '/'
            if host == u_host and u_path.startswith(path):
                return True
        return False


URLTool.__doc__ = BaseTool.__doc__

InitializeClass(URLTool)
