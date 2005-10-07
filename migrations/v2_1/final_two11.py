from Products.MimetypesRegistry.Extensions.Install import fixUpSMIGlobs
from Products.CMFCore.utils import getToolByName

def final_two11(portal):
    """2.1-final -> 2.1.1
    """
    out = []
    fixUpSMIGlobs(portal)

    # Update path index for new EPI version
    reindexPathIndex(portal, out)

    return out


def reindexPathIndex(portal, out):
    """Rebuilds the path index."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        if ('path' in catalog.indexes() and
           getattr(catalog.Indexes['path'], '_index_parents', None) is None):
            # Reduce threshold for the reindex run
            old_threshold = catalog.threshold
            pg_threshold = getattr(catalog, 'pgthreshold', 0)
            catalog.pgthreshold = 300
            catalog.threshold = 2000
            catalog.clearIndex('path')
            catalog.manage_reindexIndex(ids=['path'])
            catalog.threshold = old_threshold
            catalog.pgthreshold = pg_threshold
            out.append("Reindexed path index.")