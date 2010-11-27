import timeit

from Testing.makerequest import makerequest
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from Products.CMFCore.tests.base.security import PermissiveSecurityPolicy
from Products.CMFCore.tests.base.security import OmnipotentUser

from Products.Archetypes.tests.utils import populateFolder
from Products.CMFPlone.browser import navigation

def setup(app, path):
    _policy = PermissiveSecurityPolicy()
    _oldpolicy = setSecurityPolicy(_policy)
    newSecurityManager(None, OmnipotentUser().__of__(app.acl_users))
    site = app.unrestrictedTraverse(path)
    populateFolder(site, 'Folder', 'Document')
    return site

if __name__ == '__main__':
    # run this under "zopectl run misc.py /path/to/Plone"
    import sys

    app = makerequest(app)
    site = setup(app, sys.argv[1])
    request = site.REQUEST

    obj = site.unrestrictedTraverse('folder2/folder22/folder222/doc2222')

    def catalog():
        return navigation.CatalogNavigationBreadcrumbs(
            obj, request).breadcrumbs()

    def physical():
        return navigation.PhysicalNavigationBreadcrumbs(
            obj, request).breadcrumbs()

    times = int(sys.argv[2])

    timer = timeit.Timer('catalog()', 'from __main__ import catalog')
    print 'catalog-based:', timer.timeit(times)

    timer = timeit.Timer('physical()', 'from __main__ import physical')
    print 'physical-based:', timer.timeit(times)
