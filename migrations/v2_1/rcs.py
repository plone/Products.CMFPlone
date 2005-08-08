from alphas import reindexCatalog, indexMembersFolder, indexNewsFolder, \
                    indexEventsFolder, addIs_FolderishMetadata


def rc1_rc2(portal):
    """2.1-beta1 -> 2.1-beta2
    """
    out = []
    reindex = 0

    # Re-add metadata column to indicate whether an object is folderish
    reindex += addIs_FolderishMetadata(portal, out)

    # FIXME: *Must* be called after reindexCatalog.
    # In tests, reindexing loses the folders for some reason...

    # Rebuild catalog
    if reindex:
        reindexCatalog(portal, out)

    # Make sure the Members folder is cataloged
    indexMembersFolder(portal, out)

    # Make sure the News folder is cataloged
    indexNewsFolder(portal, out)

    # Make sure the Events folder is cataloged
    indexEventsFolder(portal, out)

    return out