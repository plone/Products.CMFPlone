from Products.CMFCore.utils import getToolByName

def three0_alpha1(portal):
    """2.5 -> 3.0-alpha1
    """
    out = [ ]

    # Add indexes for interfaces to the portal catalog
    addInterfaceIndices(portal, out)

    return out


def addInterfaceIndices(portal, out):
    """Add indexes for interfaces to the portal catalog.
    """

    catalog=getToolByName(self, 'portal_catalog')
    indeces=catalog.indexes()
    for index in [ 'object_iplements', 'object_adapts_to' ]:
        if index not in indices:
            catalog.addIndex(index, 'KeywordIndex')
            out.append('Added %s index to portal_catalog' % index)

