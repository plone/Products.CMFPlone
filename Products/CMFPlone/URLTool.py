from Products.CMFCore.URLTool import URLTool as BaseTool
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

from urlparse import urlparse


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
        """
        p_url = self()
        portal_path = urlparse(p_url)[0:3]
        url_path = urlparse(url)[0:3]
        p = {#'protocol':portal_path[0],
             'host':portal_path[1],
             'path':portal_path[2]}
        u = {#'protocol':url_path[0],
             'host':url_path[1],
             'path':url_path[2]}
        # check for urls without protocol (i.e. relative urls), or urls with
        # the same host and path.

        if not u['host'] and not u['path'].startswith('/'): #relatively relative url!
            #url is a relative path that needs to be checked. URLs that start with / can be quickly checked
            #urls that start with ../ need to have a bit of traversal
            if u['path'].startswith('.'):
                if context is None:
                    return True #old behavior
                else: #gentlemen, start your parsing engines
                    if not context.isPrincipiaFolderish:
                        useurl = context.aq_parent.absolute_url()
                    else:
                        useurl = context.absolute_url()
                    currpath = urlparse(useurl)[2].split('/') #just the path
                    for node in u['path'].split('/'): #path is something like "../../target"
                        if node == '..':
                            if currpath:
                                currpath.pop()
                            else: #we have more ../ than in the current context, we can't be in the portal
                                return False
                        elif node == '.':
                            continue
                        else: #We shouldn't have to deal with crazy urls like ../../somefolder/../otherfolder/../content
                            #add the current node to give us a bit more breathing room, in case somone was silly and used the name of the portal in the relative path
                            return ('/'.join(currpath)+'/'+node).startswith(p['path'])
            else: #url is in the form: path/to/another/object.jpg
                return True
        else:
            return (p['host'] == u['host'] or not u['host']) and u['path'].startswith(p['path'])

URLTool.__doc__ = BaseTool.__doc__

InitializeClass(URLTool)
