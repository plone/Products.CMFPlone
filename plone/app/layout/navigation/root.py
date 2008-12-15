from Acquisition import aq_base

from plone.app.layout.navigation.interfaces import INavigationRoot

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils

def getNavigationRoot(context, relativeRoot=None):
    """Get the path to the root of the navigation tree. If context or one of
    its parents until (but not including) the portal root implements
    INavigationRoot, return this.

    Otherwise, if an explicit root is set in navtree_properties or given as
    relativeRoot, use this. If the property is not set or is set to '/', use 
    the portal root.
    """

    portal_url = getToolByName(context, 'portal_url')
    
    if not relativeRoot:
        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        relativeRoot = navtree_properties.getProperty('root', None)

    portal = portal_url.getPortalObject()
    obj = getNavigationRootObject(context, portal)
    if INavigationRoot.providedBy(obj) and aq_base(obj) is not aq_base(portal):
        return '/'.join(obj.getPhysicalPath())

    rootPath = relativeRoot
    portalPath = portal_url.getPortalPath()
    contextPath = '/'.join(context.getPhysicalPath())

    if rootPath:
        if rootPath == '/':
            return portalPath
        else:
            if len(rootPath) > 1 and rootPath[0] == '/':
                return portalPath + rootPath
            else:
                return portalPath

    # This code is stolen from Sprout, but it's unclear exactly how it
    # should work and the test from Sprout isn't directly transferable
    # to testNavTree.py, since it's testing something slightly different.
    # Hoping Sidnei or someone else with a real use case can do this.
    # The idea is that if the 'root' variable is set to '', you'll get
    # the virtual root. This should probably also be used by the default
    # search, as well as the tabs and breadcrumbs. Also, the text in
    # prefs_navigation_form.cpt should be updated if this is re-enabled.
    #
    # Attempt to get use the virtual host root as root if an explicit
    # root is not set
    # if rootPath == '':
    #    request = getattr(context, 'REQUEST', None)
    #    if request is not None:
    #        vroot = request.get('VirtualRootPhysicalPath', None)
    #        if vroot is not None:
    #            return '/'.join(('',) + vroot[len(portalPath):])

    # Fall back on the portal root
    if not rootPath:
        return portalPath

def getNavigationRootObject(context, portal):
    obj = context
    while not INavigationRoot.providedBy(obj) and aq_base(obj) is not aq_base(portal):
        obj = utils.parent(obj)
    return obj