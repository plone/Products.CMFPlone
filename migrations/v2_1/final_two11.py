def final_two11(portal):
    """2.1-final -> 2.1.1
    """
    from Products.MimetypesRegistry.Extensions.Install import fixUpSMIGlobs
    out = []
    fixUpSMIGlobs(portal)

    # Update path index for new EPI version
    reindexPathIndex(portal, out)

    return out

def reindexPathIndex(portal, out):
    """Rebuilds the path index."""
    from Products.ZCatalog.ZCatalog import ZCatalog
    for catalog in portal.objectValues():
        if not isinstance(catalog, ZCatalog):
            # catalog is not really a catalog
            continue
        for name,index in catalog.Indexes.objectItems():
            if (index.meta_type == "ExtendedPathIndex" and
            getattr(catalog.Indexes._getOb('path', None), '_index_parents', None) is None):
                # Reduce threshold for the reindex run
                old_threshold = catalog.threshold
                pg_threshold = getattr(catalog, 'pgthreshold', 0)
                catalog.pgthreshold = 300
                catalog.threshold = 2000
                catalog.clearIndex(name)
                catalog.manage_reindexIndex(ids=[name])
                catalog.threshold = old_threshold
                catalog.pgthreshold = pg_threshold
                out.append("Reindexed %s index in catalog %s."%(name, catalog.getId()))
