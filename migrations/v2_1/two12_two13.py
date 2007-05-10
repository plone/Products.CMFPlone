from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.migrations.v3_0.alphas import enableZope3Site
from Products.CMFPlone.migrations.v3_0.alphas import registerToolsAsUtilities


def two12_two13(portal):
    """2.1.2 -> 2.1.3
    """
    out = []

    # Make the portal a Zope3 site
    enableZope3Site(portal, out)

    # register some tools as utilities
    registerToolsAsUtilities(portal, out)

    # Put navtree properties in a sensible state
    normalizeNavtreeProperties(portal, out)

    # Remove vcXMLRPC.js from ResourceRegistries
    removeVcXMLRPC(portal, out)

    # Required due to a fix in PortalTransforms...
    migtool = getToolByName(portal, 'portal_migration')
    migtool._needRecatalog = True

    # add icons for copy, cut, paste and delete
    addActionDropDownMenuIcons(portal, out)

    return out


def normalizeNavtreeProperties(portal, out):
    """Remove unused navtree properties, add 'name' and 'root' properties. Set
    bottomLevel to 0 if it's 65535 (the old marker)
    """
    toRemove = ['skipIndex_html', 'showMyUserFolderOnly', 'showFolderishSiblingsOnly',
                'showFolderishChildrenOnly', 'showNonFolderishObject', 'showTopicResults',
                'rolesSeeContentView', 'rolesSeeUnpublishedContent', 'rolesSeeContentsView', 
                'batchSize', 'sortCriteria', 'croppingLength', 'forceParentsInBatch', 
                'rolesSeeHiddenContent', 'typesLinkToFolderContents']
    toAdd = {'name' : ('string', ''), 
             'root' : ('string', '/'), 
             'currentFolderOnlyInNavtree' : ('boolean', False)}
    portal_properties = getToolByName(portal, 'portal_properties', None)
    if portal_properties is not None:
        navtree_properties = getattr(portal_properties, 'navtree_properties', None)
        if navtree_properties is not None:
            for property in toRemove:
                if navtree_properties.getProperty(property, None) is not None:
                    navtree_properties._delProperty(property)
            for property, value in toAdd.items():
                if navtree_properties.getProperty(property, None) is None:
                    navtree_properties._setProperty(property, value[1], value[0])
            bottomLevel = navtree_properties.getProperty('bottomLevel', None)
            if bottomLevel == 65535:
                navtree_properties.manage_changeProperties(bottomLevel = 0)


def removeVcXMLRPC(portal, out):
    """Remove vcXMLRPC.js from ResourceRegistries
    """
    jsreg = getToolByName(portal, 'portal_javascripts', None)
    if jsreg is not None:
        if 'vcXMLRPC.js' in jsreg.getResourceIds():
            jsreg.unregisterResource('vcXMLRPC.js')
            out.append('Removed vcXMLRPC.js')


def addActionDropDownMenuIcons(portal, out):
    """Add icons for copy, cut, paste and delete
    """
    ai=getToolByName(portal, 'portal_actionicons', None)
    if ai is None:
        return
    icons = dict([
        ((x.getCategory(), x.getActionId()), x)
        for x in ai.listActionIcons()
    ])
    added = False
    if ('object_buttons', 'cut') not in icons:
        ai.addActionIcon('object_buttons', 'cut', 'cut_icon.gif', 'Cut')
        added = True
    else:
        ai.updateActionIcon('object_buttons', 'cut', 'cut_icon.gif', 'Cut')
    if ('object_buttons', 'copy') not in icons:
        ai.addActionIcon('object_buttons', 'copy', 'copy_icon.gif', 'Copy')
        added = True
    else:
        ai.updateActionIcon('object_buttons', 'copy', 'copy_icon.gif', 'Copy')
    if ('object_buttons', 'paste') not in icons:
        ai.addActionIcon('object_buttons', 'paste', 'paste_icon.gif', 'Paste')
        added = True
    else:
        ai.updateActionIcon('object_buttons', 'paste', 'paste_icon.gif', 'Paste')
    if ('object_buttons', 'delete') not in icons:
        ai.addActionIcon('object_buttons', 'delete', 'delete_icon.gif', 'Delete')
        added = True
    else:
        ai.updateActionIcon('object_buttons', 'delete', 'delete_icon.gif', 'Delete')
    if added:
        out.append('Added icons for copy, cut, paste and delete')
    else:
        out.append('Updated icons for copy, cut, paste and delete')


def reindexCatalog(portal, out):
    """Rebuilds the portal_catalog."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        # Reduce threshold for the reindex run
        old_threshold = catalog.threshold
        pg_threshold = getattr(catalog, 'pgthreshold', 0)
        catalog.pgthreshold = 300
        catalog.threshold = 2000
        catalog.refreshCatalog(clear=1)
        catalog.threshold = old_threshold
        catalog.pgthreshold = pg_threshold
        out.append("Reindexed portal_catalog.")


def indexMembersFolder(portal, out):
    """Makes sure the Members folder is cataloged."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        membershipTool = getToolByName(portal, 'portal_membership', None)
        if membershipTool is not None:
            members = membershipTool.getMembersFolder()
            if members is not None:
                members.indexObject()
                out.append('Recataloged Members folder.')

