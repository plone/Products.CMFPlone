"""
$Id$
"""

from sets import Set
from Products.CMFPlone.utils import transaction

def cleanUpCatalog(catalog, out):
    _cat = catalog._catalog
    print >> out, "calculating inconsistencies on metadata trees..."
    data_rids = Set(_cat.data.keys())
    path_rids = Set(_cat.paths.keys())
    uids_rids = Set(_cat.uids.values())

    good_rids = data_rids & path_rids & uids_rids
    bad_rids = (data_rids | path_rids | uids_rids) - good_rids
    print >> out, "%s inconsistent entries detected" % len(bad_rids)
    pf_rids = Set()
    bad_paths = Set()
    for rid, path in _cat.paths.items():
        if "portal_factory/" in path:
            pf_rids.add(rid)
            bad_paths.add(path)
    for path, rid in _cat.uids.items():
        if "portal_factory/" in path:
            pf_rids.add(rid)
            bad_paths.add(path)
        if rid in bad_rids:
            bad_paths.add(path)
    pathIndex = _cat.getIndex('path')
    p_args = dict(query='portal_factory', level=-1)
    pf_rids |= Set(pathIndex._apply_index(dict(path=p_args))[0].keys())
    print >> out, "%s portal_factory entries detected" % len(pf_rids)
    bad_rids |= pf_rids
    print >> out, "cleaning up uids..."
    for path in bad_paths:
        try:
            del _cat.uids[path]
        except KeyError:
            pass
    print >> out, "cleaning up data and paths and indexes..."
    indexes = [_cat.getIndex(name) for name in _cat.indexes.keys()]
    for rid in bad_rids:
        try:
            del _cat.paths[rid]
        except KeyError:
            pass
        try:
            del _cat.data[rid]
        except KeyError:
            pass
        for index in indexes:
            if hasattr(index, 'unindex_object'):
                index.unindex_object(rid)
    print >> out, "Done"

def removeUnreachable(catalog, out):
    _cat = catalog._catalog
    count = 0
    print >> out, "removing unreachable entries in the catalog..."
    for path in _cat.uids.keys():
        if not catalog.aq_parent.unrestrictedTraverse(path, None):
            _cat.uncatalogObject(path)
            count +=1
    print >> out, "%s entries removed" % count

if __name__ == "__main__":
    # run this under "zopectl run misc.py /path/to/Plone"
    import sys
    remove_unreachable = sys.argv[2:]
    catalog = app.unrestrictedTraverse(sys.argv[1])
    cleanUpCatalog(catalog, sys.stdout)
    if remove_unreachable:
        removeUnreachable(catalog, sys.stdout)
    transaction.commit()
