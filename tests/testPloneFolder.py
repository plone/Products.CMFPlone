#
# PloneFolder tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

try: from zExceptions import NotFound
except ImportError: NotFound = 'NotFound'
try: from zExceptions import BadRequest
except ImportError: BadRequest = 'BadRequest'


class TestPloneFolder(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        # Get rid of the .personal subfolder
        membership = self.portal.portal_membership
        self.folder._delObject(membership.personal_id)
        # Create a bunch of subfolders
        self.folder.invokeFactory('Folder', id='sub1')
        self.folder.invokeFactory('Folder', id='sub2')
        self.folder.invokeFactory('Folder', id='sub3')

    def testGetObjectPosition(self):
        self.assertEqual(self.folder.getObjectPosition('sub1'), 0)

    def testGetObjectPositionRaisesNotFound(self):
        self.assertRaises(NotFound, self.folder.getObjectPosition, 'foobar')

    def testSortOrder(self):
        self.assertEqual(self.folder.objectIds(), 
            ['sub1', 'sub2', 'sub3'])

    def testEditFolderKeepsPosition(self):
        # Cover http://plone.org/collector/2796
        self.folder.sub2.folder_edit('Foo', 'Description')
        self.assertEqual(self.folder.sub2.Title(), 'Foo')
        # Order should remain the same
        self.assertEqual(self.folder.objectIds(), 
            ['sub1', 'sub2', 'sub3'])

    def testRenameFolderKeepsPosition(self):
        # Cover http://plone.org/collector/2796
        get_transaction().commit(1) # make rename work
        self.folder.sub2.folder_edit('Foo', 'Description', id='foo')
        self.assertEqual(self.folder.foo.Title(), 'Foo')
        # Order should remain the same
        self.assertEqual(self.folder.objectIds(), 
            ['sub1', 'foo', 'sub3'])


class TestCheckIdAvailable(PloneTestCase.PloneTestCase):
    # PortalFolder.checkIdAvailable() did not properly catch
    # zExceptions.BadRequest. 
    # Fixed in CMFCore.PortalFolder, not Plone.
    
    def afterSetUp(self):
        from Products.CMFPlone.PloneUtilities import _createObjectByType
        _createObjectByType('Large Plone Folder', self.folder, 'lpf')
        self.lpf = self.folder.lpf

    def testSetObjectRaisesBadRequest(self):
        # _setObject() should raise zExceptions.BadRequest
        # on duplicate id.
        self.folder._setObject('foo', dummy.Item())
        try:
            self.folder._setObject('foo', dummy.Item())
        except BadRequest:
            pass
        except:
            # Zope < 2.7
            e,v,tb = sys.exc_info(); del tb
            if str(e) != 'Bad Request':
                raise

    def testCheckIdRaisesBadRequest(self):
        # _checkId() should raise zExceptions.BadRequest
        # on duplicate id.
        self.folder._setObject('foo', dummy.Item())
        try:
            self.folder._checkId('foo')
        except BadRequest:
            pass
        except:
            # Zope < 2.7
            e,v,tb = sys.exc_info(); del tb
            if str(e) != 'Bad Request':
                raise

    def testCheckIdAvailableCatchesBadRequest(self):
        # checkIdAvailable() should catch zExceptions.BadRequest
        self.folder._setObject('foo', dummy.Item())
        self.failIf(self.folder.checkIdAvailable('foo'))

    def testLPFSetObjectRaisesBadRequest(self):
        # _setObject() should raise zExceptions.BadRequest
        # on duplicate id.
        self.lpf._setObject('foo', dummy.Item())
        try:
            self.lpf._setObject('foo', dummy.Item())
        except BadRequest:
            pass
        except:
            # Zope < 2.7
            e,v,tb = sys.exc_info(); del tb
            if str(e) != 'Bad Request':
                raise

    def testLPFCheckIdRaisesBadRequest(self):
        # _checkId() should raise zExceptions.BadRequest
        # on duplicate id.
        self.lpf._setObject('foo', dummy.Item())
        try:
            self.lpf._checkId('foo')
        except BadRequest:
            pass
        except:
            # Zope < 2.7
            e,v,tb = sys.exc_info(); del tb
            if str(e) != 'Bad Request':
                raise

    def testLPFCheckIdAvailableCatchesBadRequest(self):
        # checkIdAvailable() should catch zExceptions.BadRequest
        self.lpf._setObject('foo', dummy.Item())
        self.failIf(self.lpf.checkIdAvailable('foo'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPloneFolder))
    suite.addTest(makeSuite(TestCheckIdAvailable))
    return suite

if __name__ == '__main__':
    framework()
