from Products.CMFPlone.tests import PloneTestCase

from Products.CMFCore.utils import getToolByName

from plone.app.layout.navigation.interfaces import INavigationRoot

from plone.app.layout.navigation.navtree import NavtreeStrategyBase
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.navigation.root import getNavigationRoot

from zope.interface import directlyProvides
from zope.interface import implementer


from Products.CMFPlone.PloneFolder import PloneFolder
from Products.CMFPlone.interfaces import INonStructuralFolder

default_user = PloneTestCase.default_user



@implementer(INonStructuralFolder)
class DummyNonStructuralFolder(PloneFolder):
    pass


class TestFolderTree(PloneTestCase.PloneTestCase):
    '''Test the basic buildFolderTree method'''

    def afterSetUp(self):
        self.populateSite()
        self.setupAuthenticator()

    def populateSite(self):
        """
            Portal
            +-doc1
            +-doc2
            +-doc3
            +-folder1
              +-doc11
              +-doc12
              +-doc13
            +-link1
            +-folder2
              +-doc21
              +-doc22
              +-doc23
              +-file21
              +-folder21
                +-doc211
                +-doc212
        """
        self.setRoles(['Manager'])

        for item in self.portal.getFolderContents():
            self.portal._delObject(item.getId)

        self.portal.invokeFactory('Document', 'doc1')
        self.portal.invokeFactory('Document', 'doc2')
        self.portal.invokeFactory('Document', 'doc3')
        self.portal.invokeFactory('Folder', 'folder1')
        self.portal.invokeFactory('Link', 'link1')
        self.portal.link1.remoteUrl = 'http://plone.org'
        self.portal.link1.reindexObject()
        folder1 = getattr(self.portal, 'folder1')
        folder1.invokeFactory('Document', 'doc11')
        folder1.invokeFactory('Document', 'doc12')
        folder1.invokeFactory('Document', 'doc13')
        self.portal.invokeFactory('Folder', 'folder2')
        folder2 = getattr(self.portal, 'folder2')
        folder2.invokeFactory('Document', 'doc21')
        folder2.invokeFactory('Document', 'doc22')
        folder2.invokeFactory('Document', 'doc23')
        folder2.invokeFactory('File', 'file21')
        folder2.invokeFactory('Folder', 'folder21')
        folder21 = getattr(folder2, 'folder21')
        folder21.invokeFactory('Document', 'doc211')
        folder21.invokeFactory('Document', 'doc212')
        self.setRoles(['Member'])

    # Get from the root, filters

    def testGetFromRoot(self):
        tree = buildFolderTree(self.portal)['children']
        rootPath = '/'.join(self.portal.getPhysicalPath())
        self.assertEqual(len(tree), 6)
        self.assertEqual(tree[0]['item'].getPath(), rootPath + '/doc1')
        self.assertEqual(tree[1]['item'].getPath(), rootPath + '/doc2')
        self.assertEqual(tree[2]['item'].getPath(), rootPath + '/doc3')
        self.assertEqual(tree[3]['item'].getPath(), rootPath + '/folder1')
        self.assertEqual(len(tree[3]['children']), 3)
        self.assertEqual(tree[3]['children'][0][
                         'item'].getPath(), rootPath + '/folder1/doc11')
        self.assertEqual(tree[3]['children'][1][
                         'item'].getPath(), rootPath + '/folder1/doc12')
        self.assertEqual(tree[3]['children'][2][
                         'item'].getPath(), rootPath + '/folder1/doc13')
        self.assertEqual(tree[4]['item'].getPath(), rootPath + '/link1')
        self.assertEqual(tree[5]['item'].getPath(), rootPath + '/folder2')
        self.assertEqual(len(tree[5]['children']), 5)
        self.assertEqual(tree[5]['children'][0][
                         'item'].getPath(), rootPath + '/folder2/doc21')
        self.assertEqual(tree[5]['children'][1][
                         'item'].getPath(), rootPath + '/folder2/doc22')
        self.assertEqual(tree[5]['children'][2][
                         'item'].getPath(), rootPath + '/folder2/doc23')
        self.assertEqual(tree[5]['children'][3][
                         'item'].getPath(), rootPath + '/folder2/file21')
        self.assertEqual(tree[5]['children'][4][
                         'item'].getPath(), rootPath + '/folder2/folder21')
        self.assertEqual(len(tree[5]['children'][4]['children']), 2)
        self.assertEqual(tree[5]['children'][4]['children'][0][
                         'item'].getPath(), rootPath + '/folder2/folder21/doc211')
        self.assertEqual(tree[5]['children'][4]['children'][1][
                         'item'].getPath(), rootPath + '/folder2/folder21/doc212')

    def testGetFromRootWithSpecifiedRoot(self):
        rootPath = '/'.join(self.portal.getPhysicalPath())
        strategy = NavtreeStrategyBase()
        strategy.rootPath = rootPath + '/folder1'
        tree = buildFolderTree(self.portal, strategy=strategy)['children']
        self.assertEqual(len(tree), 3)
        self.assertEqual(tree[0]['item'].getPath(),
                         rootPath + '/folder1/doc11')
        self.assertEqual(tree[1]['item'].getPath(),
                         rootPath + '/folder1/doc12')
        self.assertEqual(tree[2]['item'].getPath(),
                         rootPath + '/folder1/doc13')

    def testGetFromRootWithNodeFilter(self):
        class Strategy(NavtreeStrategyBase):

            def nodeFilter(self, node):
                return ('doc' not in node['item'].getId)
        tree = buildFolderTree(self.portal, strategy=Strategy())['children']
        rootPath = '/'.join(self.portal.getPhysicalPath())
        self.assertEqual(len(tree), 3)
        self.assertEqual(tree[0]['item'].getPath(), rootPath + '/folder1')
        self.assertEqual(len(tree[0]['children']), 0)
        self.assertEqual(tree[1]['item'].getPath(), rootPath + '/link1')
        self.assertEqual(tree[2]['item'].getPath(), rootPath + '/folder2')
        self.assertEqual(len(tree[2]['children']), 2)
        self.assertEqual(tree[2]['children'][0][
                         'item'].getPath(), rootPath + '/folder2/file21')
        self.assertEqual(tree[2]['children'][1][
                         'item'].getPath(), rootPath + '/folder2/folder21')
        self.assertEqual(len(tree[2]['children'][1]['children']), 0)

    def testGetFromRootWithNodeFilterOnFolder(self):
        class Strategy(NavtreeStrategyBase):

            def nodeFilter(self, node):
                return ('folder' not in node['item'].getId)
        tree = buildFolderTree(self.portal, strategy=Strategy())['children']
        rootPath = '/'.join(self.portal.getPhysicalPath())
        self.assertEqual(len(tree), 4)
        self.assertEqual(tree[0]['item'].getPath(), rootPath + '/doc1')
        self.assertEqual(tree[1]['item'].getPath(), rootPath + '/doc2')
        self.assertEqual(tree[2]['item'].getPath(), rootPath + '/doc3')
        self.assertEqual(tree[3]['item'].getPath(), rootPath + '/link1')

    def testGetFromRootWithSubtreeFilter(self):
        class Strategy(NavtreeStrategyBase):

            def subtreeFilter(self, node):
                return ('folder2' != node['item'].getId)
        tree = buildFolderTree(self.portal, strategy=Strategy())['children']
        rootPath = '/'.join(self.portal.getPhysicalPath())
        self.assertEqual(len(tree), 6)
        self.assertEqual(tree[0]['item'].getPath(), rootPath + '/doc1')
        self.assertEqual(tree[1]['item'].getPath(), rootPath + '/doc2')
        self.assertEqual(tree[2]['item'].getPath(), rootPath + '/doc3')
        self.assertEqual(tree[3]['item'].getPath(), rootPath + '/folder1')
        self.assertEqual(len(tree[3]['children']), 3)
        self.assertEqual(tree[3]['children'][0][
                         'item'].getPath(), rootPath + '/folder1/doc11')
        self.assertEqual(tree[3]['children'][1][
                         'item'].getPath(), rootPath + '/folder1/doc12')
        self.assertEqual(tree[3]['children'][2][
                         'item'].getPath(), rootPath + '/folder1/doc13')
        self.assertEqual(tree[4]['item'].getPath(), rootPath + '/link1')
        self.assertEqual(tree[5]['item'].getPath(), rootPath + '/folder2')
        self.assertEqual(len(tree[5]['children']), 0)

    def testNonFolderishObjectNotExpanded(self):
        self.setRoles(['Manager'])
        f = DummyNonStructuralFolder('ns_folder')
        self.portal._setObject('ns_folder', f)
        ns_folder = self.portal.ns_folder
        self.portal.portal_catalog.indexObject(self.portal.ns_folder)
        ns_folder.invokeFactory('Document', 'doc')
        self.setRoles(['Member'])
        tree = buildFolderTree(self.portal, self.portal.ns_folder)['children']
        rootPath = '/'.join(self.portal.getPhysicalPath())
        self.assertEqual(tree[-1]['item'].getPath(), rootPath + '/ns_folder')
        self.assertEqual(len(tree[-1]['children']), 0)

    def testShowAllParentsOverridesNonFolderishObjectNotExpanded(self):
        strategy = NavtreeStrategyBase()
        strategy.showAllParents = True
        self.setRoles(['Manager'])
        f = DummyNonStructuralFolder('ns_folder')
        self.portal._setObject('ns_folder', f)
        ns_folder = self.portal.ns_folder
        self.portal.portal_catalog.indexObject(self.portal.ns_folder)
        ns_folder.invokeFactory('Document', 'doc')
        self.setRoles(['Member'])
        tree = buildFolderTree(self.portal, self.portal.ns_folder.doc,
                               strategy=strategy)['children']
        rootPath = '/'.join(self.portal.getPhysicalPath())
        self.assertEqual(tree[-1]['item'].getPath(), rootPath + '/ns_folder')
        self.assertEqual(len(tree[-1]['children']), 1)
        self.assertEqual(tree[-1]['children'][0]
                         ['item'].getPath(), rootPath + '/ns_folder/doc')

    def testGetWithRootContext(self):
        tree = buildFolderTree(self.portal, obj=self.portal)['children']
        rootPath = '/'.join(self.portal.getPhysicalPath())
        self.assertEqual(len(tree), 6)
        self.assertEqual(tree[0]['item'].getPath(), rootPath + '/doc1')
        self.assertEqual(tree[1]['item'].getPath(), rootPath + '/doc2')
        self.assertEqual(tree[2]['item'].getPath(), rootPath + '/doc3')
        self.assertEqual(tree[3]['item'].getPath(), rootPath + '/folder1')
        self.assertEqual(len(tree[3]['children']), 3)
        self.assertEqual(tree[3]['children'][0][
                         'item'].getPath(), rootPath + '/folder1/doc11')
        self.assertEqual(tree[3]['children'][1][
                         'item'].getPath(), rootPath + '/folder1/doc12')
        self.assertEqual(tree[3]['children'][2][
                         'item'].getPath(), rootPath + '/folder1/doc13')
        self.assertEqual(tree[4]['item'].getPath(), rootPath + '/link1')
        self.assertEqual(tree[5]['item'].getPath(), rootPath + '/folder2')
        self.assertEqual(len(tree[5]['children']), 5)
        self.assertEqual(tree[5]['children'][0][
                         'item'].getPath(), rootPath + '/folder2/doc21')
        self.assertEqual(tree[5]['children'][1][
                         'item'].getPath(), rootPath + '/folder2/doc22')
        self.assertEqual(tree[5]['children'][2][
                         'item'].getPath(), rootPath + '/folder2/doc23')
        self.assertEqual(tree[5]['children'][3][
                         'item'].getPath(), rootPath + '/folder2/file21')
        self.assertEqual(tree[5]['children'][4][
                         'item'].getPath(), rootPath + '/folder2/folder21')
        self.assertEqual(len(tree[5]['children'][4]['children']), 2)
        self.assertEqual(tree[5]['children'][4]['children'][0][
                         'item'].getPath(), rootPath + '/folder2/folder21/doc211')
        self.assertEqual(tree[5]['children'][4]['children'][1][
                         'item'].getPath(), rootPath + '/folder2/folder21/doc212')

    def testGetFromFixed(self):
        rootPath = '/'.join(self.portal.getPhysicalPath())
        query = {'path': rootPath + '/folder1'}
        tree = buildFolderTree(self.portal, query=query)['children']
        self.assertEqual(len(tree), 3)
        self.assertEqual(tree[0]['item'].getPath(),
                         rootPath + '/folder1/doc11')
        self.assertEqual(tree[1]['item'].getPath(),
                         rootPath + '/folder1/doc12')
        self.assertEqual(tree[2]['item'].getPath(),
                         rootPath + '/folder1/doc13')

    def testGetFromFixedAndDepth(self):
        rootPath = '/'.join(self.portal.getPhysicalPath())
        query = {'path': rootPath + '/folder2', 'depth': 1}
        tree = buildFolderTree(self.portal, query=query)['children']
        self.assertEqual(len(tree), 5)
        self.assertEqual(tree[0]['item'].getPath(),
                         rootPath + '/folder2/doc21')
        self.assertEqual(tree[1]['item'].getPath(),
                         rootPath + '/folder2/doc22')
        self.assertEqual(tree[2]['item'].getPath(),
                         rootPath + '/folder2/doc23')
        self.assertEqual(tree[3]['item'].getPath(),
                         rootPath + '/folder2/file21')
        self.assertEqual(tree[4]['item'].getPath(),
                         rootPath + '/folder2/folder21')

    def testGetFromRootWithCurrent(self):
        context = self.portal.folder2.doc21
        tree = buildFolderTree(self.portal, obj=context)['children']
        self.assertEqual(len(tree), 6)
        for t in tree:
            if t['item'].getId == 'folder2':
                self.assertEqual(t['currentItem'], False)
                self.assertEqual(t['currentParent'], True)
                for c in t['children']:
                    if c['item'].getId == 'doc21':
                        self.assertEqual(c['currentItem'], True)
                        self.assertEqual(c['currentParent'], False)
                    else:
                        self.assertEqual(c['currentItem'], False)
                        self.assertEqual(c['currentParent'], False)
            else:
                self.assertEqual(t['currentItem'], False)
                self.assertEqual(t['currentParent'], False)

    def testGetFromRootIgnoresDefaultPages(self):
        self.portal.folder1.setDefaultPage('doc12')
        self.portal.folder2.setDefaultPage('doc21')
        tree = buildFolderTree(self.portal)['children']
        rootPath = '/'.join(self.portal.getPhysicalPath())
        self.assertEqual(len(tree), 6)
        self.assertEqual(tree[0]['item'].getPath(), rootPath + '/doc1')
        self.assertEqual(tree[1]['item'].getPath(), rootPath + '/doc2')
        self.assertEqual(tree[2]['item'].getPath(), rootPath + '/doc3')
        self.assertEqual(tree[3]['item'].getPath(), rootPath + '/folder1')
        self.assertEqual(len(tree[3]['children']), 2)
        self.assertEqual(tree[3]['children'][0][
                         'item'].getPath(), rootPath + '/folder1/doc11')
        self.assertEqual(tree[3]['children'][1][
                         'item'].getPath(), rootPath + '/folder1/doc13')
        self.assertEqual(tree[4]['item'].getPath(), rootPath + '/link1')
        self.assertEqual(tree[5]['item'].getPath(), rootPath + '/folder2')
        self.assertEqual(len(tree[5]['children']), 4)
        self.assertEqual(tree[5]['children'][0][
                         'item'].getPath(), rootPath + '/folder2/doc22')
        self.assertEqual(tree[5]['children'][1][
                         'item'].getPath(), rootPath + '/folder2/doc23')
        self.assertEqual(tree[5]['children'][2][
                         'item'].getPath(), rootPath + '/folder2/file21')
        self.assertEqual(tree[5]['children'][3][
                         'item'].getPath(), rootPath + '/folder2/folder21')
        self.assertEqual(len(tree[5]['children'][3]['children']), 2)
        self.assertEqual(tree[5]['children'][3]['children'][0][
                         'item'].getPath(), rootPath + '/folder2/folder21/doc211')
        self.assertEqual(tree[5]['children'][3]['children'][1][
                         'item'].getPath(), rootPath + '/folder2/folder21/doc212')

    def testGetFromRootWithCurrentIsDefaultPage(self):
        self.portal.folder2.setDefaultPage('doc21')
        context = self.portal.folder2.doc21
        tree = buildFolderTree(self.portal, obj=context)['children']
        for t in tree:
            if t['item'].getId == 'folder2':
                self.assertEqual(t['currentItem'], True)
                self.assertEqual(t['currentParent'], False)
                for c in t['children']:
                    self.assertEqual(c['currentItem'], False)
                    self.assertEqual(c['currentParent'], False)
            else:
                self.assertEqual(t['currentItem'], False)
                self.assertEqual(t['currentParent'], False)

    def testGetFromRootWithCustomQuery(self):
        query = {'portal_type': 'Document'}
        tree = buildFolderTree(self.portal, query=query)['children']
        rootPath = '/'.join(self.portal.getPhysicalPath())
        self.assertEqual(len(tree), 3)
        self.assertEqual(tree[0]['item'].getPath(), rootPath + '/doc1')
        self.assertEqual(tree[1]['item'].getPath(), rootPath + '/doc2')
        self.assertEqual(tree[2]['item'].getPath(), rootPath + '/doc3')

    def testGetFromRootWithDecoratorFactory(self):
        class Strategy(NavtreeStrategyBase):

            def decoratorFactory(self, node):
                node['foo'] = True
                return node
        tree = buildFolderTree(self.portal, strategy=Strategy())['children']
        self.assertEqual(tree[0]['foo'], True)

    def testShowAllParents(self):
        strategy = NavtreeStrategyBase()
        strategy.showAllParents = True
        query = {'portal_type': 'Folder'}
        context = self.portal.folder1.doc11
        tree = buildFolderTree(self.portal, query=query, obj=context,
                               strategy=strategy)['children']
        rootPath = '/'.join(self.portal.getPhysicalPath())
        self.assertEqual(len(tree), 2)
        self.assertEqual(tree[0]['item'].getPath(), rootPath + '/folder1')
        self.assertEqual(len(tree[0]['children']), 1)
        self.assertEqual(tree[0]['children'][0][
                         'item'].getPath(), rootPath + '/folder1/doc11')
        self.assertEqual(tree[1]['item'].getPath(), rootPath + '/folder2')
        self.assertEqual(len(tree[1]['children']), 1)
        self.assertEqual(tree[1]['children'][0][
                         'item'].getPath(), rootPath + '/folder2/folder21')

    def testShowAllParentsWithRestrictedParent(self):
        strategy = NavtreeStrategyBase()
        strategy.showAllParents = True
        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.doActionFor(self.portal.folder1, 'hide')
        self.portal.folder1.reindexObject()
        query = {'portal_type': 'Folder'}
        context = self.portal.folder1.doc11
        tree = buildFolderTree(self.portal, query=query, obj=context,
                               strategy=strategy)['children']
        rootPath = '/'.join(self.portal.getPhysicalPath())
        self.assertEqual(len(tree), 2)
        self.assertEqual(tree[0]['item'].getPath(), rootPath + '/folder1')
        self.assertEqual(len(tree[0]['children']), 1)
        self.assertEqual(tree[0]['children'][0][
                         'item'].getPath(), rootPath + '/folder1/doc11')
        self.assertEqual(tree[1]['item'].getPath(), rootPath + '/folder2')
        self.assertEqual(len(tree[1]['children']), 1)
        self.assertEqual(tree[1]['children'][0][
                         'item'].getPath(), rootPath + '/folder2/folder21')

    def testShowAllParentsWithParentNotInCatalog(self):
        strategy = NavtreeStrategyBase()
        strategy.showAllParents = True
        self.portal.folder1.unindexObject()
        query = {'portal_type': 'Folder'}
        context = self.portal.folder1.doc11
        tree = buildFolderTree(self.portal, query=query, obj=context,
                               strategy=strategy)['children']
        rootPath = '/'.join(self.portal.getPhysicalPath())
        # XXX: Ideally, this shouldn't happen, we should get a dummy node, but
        # there's no way to do that with the catalog
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[0]['item'].getPath(), rootPath + '/folder2')

    def testDontShowAllParents(self):
        strategy = NavtreeStrategyBase()
        strategy.showAllParents = False
        query = {'portal_type': 'Folder'}
        context = self.portal.folder1.doc11
        tree = buildFolderTree(self.portal, query=query, obj=context,
                               strategy=strategy)['children']
        rootPath = '/'.join(self.portal.getPhysicalPath())
        self.assertEqual(len(tree), 2)
        self.assertEqual(tree[0]['item'].getPath(), rootPath + '/folder1')
        self.assertEqual(len(tree[0]['children']), 0)
        self.assertEqual(tree[1]['item'].getPath(), rootPath + '/folder2')
        self.assertEqual(len(tree[1]['children']), 1)
        self.assertEqual(tree[1]['children'][0][
                         'item'].getPath(), rootPath + '/folder2/folder21')

    def testGetFromRootWithCurrentNavtree(self):
        context = self.portal.folder1.doc11
        query = {'path': {'query': '/'.join(context.getPhysicalPath()),
                          'navtree': 1}}
        tree = buildFolderTree(self.portal, query=query)['children']
        rootPath = '/'.join(self.portal.getPhysicalPath())
        self.assertEqual(len(tree), 6)
        self.assertEqual(tree[0]['item'].getPath(), rootPath + '/doc1')
        self.assertEqual(tree[1]['item'].getPath(), rootPath + '/doc2')
        self.assertEqual(tree[2]['item'].getPath(), rootPath + '/doc3')
        self.assertEqual(tree[3]['item'].getPath(), rootPath + '/folder1')
        self.assertEqual(len(tree[3]['children']), 3)
        self.assertEqual(tree[3]['children'][0][
                         'item'].getPath(), rootPath + '/folder1/doc11')
        self.assertEqual(tree[3]['children'][1][
                         'item'].getPath(), rootPath + '/folder1/doc12')
        self.assertEqual(tree[3]['children'][2][
                         'item'].getPath(), rootPath + '/folder1/doc13')
        self.assertEqual(tree[4]['item'].getPath(), rootPath + '/link1')
        self.assertEqual(tree[5]['item'].getPath(), rootPath + '/folder2')
        self.assertEqual(len(tree[5]['children']), 0)

    def testGetFromRootWithCurrentNavtreeAndStartLevel(self):
        context = self.portal.folder1.doc11
        query = {'path': {'query': '/'.join(context.getPhysicalPath()),
                          'navtree': 1,
                          'navtree_start': 2}}
        rootPath = '/'.join(self.portal.getPhysicalPath())
        tree = buildFolderTree(self.portal, query=query)['children']
        self.assertEqual(len(tree), 3)
        self.assertEqual(tree[0]['item'].getPath(),
                         rootPath + '/folder1/doc11')
        self.assertEqual(tree[1]['item'].getPath(),
                         rootPath + '/folder1/doc12')
        self.assertEqual(tree[2]['item'].getPath(),
                         rootPath + '/folder1/doc13')

    def testGetFromRootWithCurrentNavtreePruned(self):
        context = self.portal.folder1.doc11

        class Strategy(NavtreeStrategyBase):

            def subtreeFilter(self, node):
                return (node['item'].getId != 'folder1')
            showAllParents = True

        query = {'path': {'query': '/'.join(context.getPhysicalPath()),
                          'navtree': 1}}
        rootPath = '/'.join(self.portal.getPhysicalPath())
        tree = buildFolderTree(self.portal, query=query,
                               obj=context, strategy=Strategy())['children']
        self.assertEqual(len(tree), 6)
        self.assertEqual(tree[0]['item'].getPath(), rootPath + '/doc1')
        self.assertEqual(tree[1]['item'].getPath(), rootPath + '/doc2')
        self.assertEqual(tree[2]['item'].getPath(), rootPath + '/doc3')
        self.assertEqual(tree[3]['item'].getPath(), rootPath + '/folder1')
        self.assertEqual(len(tree[3]['children']), 1)
        self.assertEqual(tree[3]['children'][0][
                         'item'].getPath(), rootPath + '/folder1/doc11')
        self.assertEqual(tree[4]['item'].getPath(), rootPath + '/link1')
        self.assertEqual(tree[5]['item'].getPath(), rootPath + '/folder2')
        self.assertEqual(len(tree[5]['children']), 0)

    def testGetFromRootWithCurrentFolderishNavtreePruned(self):
        context = self.portal.folder2.folder21

        class Strategy(NavtreeStrategyBase):

            def subtreeFilter(self, node):
                return (node['item'].getId != 'folder2')
            showAllParents = True

        query = {'path': {'query': '/'.join(context.getPhysicalPath()),
                          'navtree': 1}}
        rootPath = '/'.join(self.portal.getPhysicalPath())
        tree = buildFolderTree(self.portal, query=query,
                               obj=context, strategy=Strategy())['children']
        self.assertEqual(len(tree), 6)
        self.assertEqual(tree[0]['item'].getPath(), rootPath + '/doc1')
        self.assertEqual(tree[1]['item'].getPath(), rootPath + '/doc2')
        self.assertEqual(tree[2]['item'].getPath(), rootPath + '/doc3')
        self.assertEqual(tree[3]['item'].getPath(), rootPath + '/folder1')
        self.assertEqual(len(tree[3]['children']), 0)
        self.assertEqual(tree[4]['item'].getPath(), rootPath + '/link1')
        self.assertEqual(tree[5]['item'].getPath(), rootPath + '/folder2')
        self.assertEqual(len(tree[5]['children']), 1)
        self.assertEqual(tree[5]['children'][0][
                         'item'].getPath(), rootPath + '/folder2/folder21')
        self.assertEqual(len(tree[5]['children'][0]['children']), 2)
        self.assertEqual(tree[5]['children'][0]['children'][0][
                         'item'].getPath(), rootPath + '/folder2/folder21/doc211')
        self.assertEqual(tree[5]['children'][0]['children'][1][
                         'item'].getPath(), rootPath + '/folder2/folder21/doc212')

    def testCurrentParent(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Document', 'doc')
        context = self.portal.doc1
        tree = buildFolderTree(self.portal, obj=context)['children']
        for t in tree:
            if t['item'].getId == 'doc':
                self.assertEqual(t['currentParent'], False)


class TestNavigationRoot(PloneTestCase.PloneTestCase):

    def testGetNavigationRootPropertyNotSet(self):
        self.portal.portal_registry['plone.root'] = '/'
        root = getNavigationRoot(self.portal)
        self.assertEqual(root, '/'.join(self.portal.getPhysicalPath()))

    def testGetNavigationRootPropertyEmptyNoVirtualHost(self):
        self.portal.portal_properties.navtree_properties \
            .manage_changeProperties(root='')
        root = getNavigationRoot(self.portal)
        self.assertEqual(root, '/'.join(self.portal.getPhysicalPath()))

    def testGetNavigationRootPropertyIsRoot(self):
        self.portal.portal_properties.navtree_properties \
            .manage_changeProperties(root='/')
        root = getNavigationRoot(self.portal)
        self.assertEqual(root, '/'.join(self.portal.getPhysicalPath()))

    def testGetNavigationRootPropertyIsFolder(self):
        folderPath = '/'.join(self.folder.getPhysicalPath())
        portalPath = '/'.join(self.portal.getPhysicalPath())
        relativePath = folderPath[len(portalPath):]
        self.portal.portal_registry['plone.root'] = str(relativePath)
        root = getNavigationRoot(self.portal)
        self.assertEqual(root, folderPath)

    def testGetNavigationRootWithINavigationRoot(self):
        folderPath = '/'.join(self.folder.getPhysicalPath())
        self.folder.invokeFactory('Folder', 'folder1')
        self.folder.folder1.invokeFactory('Document', 'doc1')
        directlyProvides(self.folder, INavigationRoot)
        root = getNavigationRoot(self.folder.folder1.doc1)
        self.assertEqual(root, folderPath)
