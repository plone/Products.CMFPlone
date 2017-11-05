# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent, aq_inner
from App.class_init import InitializeClass
from plone.registry.interfaces import IRegistry
from posixpath import normpath
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.URLTool import URLTool as BaseTool
from Products.CMFPlone.interfaces import ILoginSchema
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.patches.gtbn import rewrap_in_request_container
from urlparse import urlparse, urljoin
from zope.component import getUtility
import re


class URLTool(PloneBaseTool, BaseTool):

    meta_type = 'Plone URL Tool'
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/link_icon.png'

    security.declarePublic('isURLInPortal')

    def isURLInPortal(self, url, context=None):
        # Check if a given url is on the same host and contains the portal
        # path.  Used to ensure that login forms can determine relevant
        # referrers (i.e. in portal).  Also return true for some relative
        # urls if context is passed in to allow for url parsing. When context
        # is not provided, assume that relative urls are in the portal. It is
        # assumed that http://portal is the same portal as https://portal.

        # External sites listed in 'allow_external_login_sites' of
        # site_properties are also considered within the portal to allow for
        # single sign on.

        # sanitize url
        url = re.sub('^[\x00-\x20]+', '', url).strip()
        cmp_url = url.lower()
        if ('\\\\' in cmp_url or
                '<script' in cmp_url or
                '%3cscript' in cmp_url or
                'javascript:' in cmp_url or
                'javascript%3a' in cmp_url):
            return False

        p_url = self()

        _, u_host, u_path, _, _, _ = urlparse(url)
        if not u_host and not u_path.startswith('/'):
            if context is None:
                return True  # old behavior
            if not context.isPrincipiaFolderish:
                useurl = context.aq_parent.absolute_url()
            else:
                useurl = context.absolute_url()
        else:
            useurl = p_url  # when u_path.startswith('/')
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

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILoginSchema, prefix='plone')
        for external_site in settings.allow_external_login_sites:
            _, host, path, _, _, _ = urlparse(external_site)
            if not path.endswith('/'):
                path += '/'
            if host == u_host and u_path.startswith(path):
                return True
        return False

    def getPortalObject(self):
        portal = aq_parent(aq_inner(self))
        if portal is None:
            portal = getUtility(ISiteRoot)
        # Make sure portal can acquire REQUEST
        return rewrap_in_request_container(portal, context=self)


URLTool.__doc__ = BaseTool.__doc__

InitializeClass(URLTool)
