#
# Test our OrderSupport implementation
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase


class TestOrderSupport(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        # Get rid of the .personal subfolder
        membership = self.portal.portal_membership
        self.folder._delObject(membership.personal_id)
        # Add a bunch of subobjects we can order later on
        self.folder.invokeFactory('Document', id='foo')
        self.folder.invokeFactory('Document', id='bar')
        self.folder.invokeFactory('Document', id='baz')

    def testGetObjectPosition(self):
        self.assertEqual(self.folder.getObjectPosition('foo'), 0)
        self.assertEqual(self.folder.getObjectPosition('bar'), 1)
        self.assertEqual(self.folder.getObjectPosition('baz'), 2)

    def testMoveObject(self):
        self.folder.moveObjectToPosition('foo', 1)
        self.assertEqual(self.folder.getObjectPosition('bar'), 0)
        self.assertEqual(self.folder.getObjectPosition('foo'), 1)
        self.assertEqual(self.folder.getObjectPosition('baz'), 2)

    def testMoveObjectToSamePos(self):
        self.folder.moveObjectToPosition('bar', 1)
        self.assertEqual(self.folder.getObjectPosition('foo'), 0)
        self.assertEqual(self.folder.getObjectPosition('bar'), 1)
        self.assertEqual(self.folder.getObjectPosition('baz'), 2)

    def testMoveObjectToFirstPos(self):
        self.folder.moveObjectToPosition('bar', 0)
        self.assertEqual(self.folder.getObjectPosition('bar'), 0)
        self.assertEqual(self.folder.getObjectPosition('foo'), 1)
        self.assertEqual(self.folder.getObjectPosition('baz'), 2)

    def testMoveObjectToLastPos(self):
        self.folder.moveObjectToPosition('bar', 2)
        self.assertEqual(self.folder.getObjectPosition('foo'), 0)
        self.assertEqual(self.folder.getObjectPosition('baz'), 1)
        self.assertEqual(self.folder.getObjectPosition('bar'), 2)

    def testMoveObjectOutLowerBounds(self):
        # Pos will be normalized to 0
        self.folder.moveObjectToPosition('bar', -1)
        self.assertEqual(self.folder.getObjectPosition('bar'), 0)
        self.assertEqual(self.folder.getObjectPosition('foo'), 1)
        self.assertEqual(self.folder.getObjectPosition('baz'), 2)

    def testMoveObjectOutUpperBounds(self):
        # Pos will be normalized to 2
        self.folder.moveObjectToPosition('bar', 3)
        self.assertEqual(self.folder.getObjectPosition('foo'), 0)
        self.assertEqual(self.folder.getObjectPosition('baz'), 1)
        self.assertEqual(self.folder.getObjectPosition('bar'), 2)

    def testMoveObjectsUp(self):
        self.assertEqual(self.folder.moveObjectsUp(['bar']), 1)
        self.assertEqual(self.folder.getObjectPosition('bar'), 0)
        self.assertEqual(self.folder.getObjectPosition('foo'), 1)
        self.assertEqual(self.folder.getObjectPosition('baz'), 2)

    def testMoveObjectsDown(self):
        self.assertEqual(self.folder.moveObjectsDown(['bar']), 1)
        self.assertEqual(self.folder.getObjectPosition('foo'), 0)
        self.assertEqual(self.folder.getObjectPosition('baz'), 1)
        self.assertEqual(self.folder.getObjectPosition('bar'), 2)

    def testMoveObjectsToTop(self):
        self.assertEqual(self.folder.moveObjectsToTop(['bar']), 1)
        self.assertEqual(self.folder.getObjectPosition('bar'), 0)
        self.assertEqual(self.folder.getObjectPosition('foo'), 1)
        self.assertEqual(self.folder.getObjectPosition('baz'), 2)

    def testMoveObjectsToBottom(self):
        self.assertEqual(self.folder.moveObjectsToBottom(['bar']), 1)
        self.assertEqual(self.folder.getObjectPosition('foo'), 0)
        self.assertEqual(self.folder.getObjectPosition('baz'), 1)
        self.assertEqual(self.folder.getObjectPosition('bar'), 2)

    def testMoveTwoObjectsUp(self):
        self.assertEqual(self.folder.moveObjectsUp(['bar', 'baz']), 2)
        self.assertEqual(self.folder.getObjectPosition('bar'), 0)
        self.assertEqual(self.folder.getObjectPosition('baz'), 1)
        self.assertEqual(self.folder.getObjectPosition('foo'), 2)

    def testMoveTwoObjectsDown(self):
        self.assertEqual(self.folder.moveObjectsDown(['foo', 'bar']), 2)
        self.assertEqual(self.folder.getObjectPosition('baz'), 0)
        self.assertEqual(self.folder.getObjectPosition('foo'), 1)
        self.assertEqual(self.folder.getObjectPosition('bar'), 2)

    def testMoveTwoObjectsToTop(self):
        self.assertEqual(self.folder.moveObjectsToTop(['bar', 'baz']), 2)
        self.assertEqual(self.folder.getObjectPosition('bar'), 0)
        self.assertEqual(self.folder.getObjectPosition('baz'), 1)
        self.assertEqual(self.folder.getObjectPosition('foo'), 2)

    def testMoveTwoObjectsToBottom(self):
        self.assertEqual(self.folder.moveObjectsToBottom(['foo', 'bar']), 2)
        self.assertEqual(self.folder.getObjectPosition('baz'), 0)
        self.assertEqual(self.folder.getObjectPosition('foo'), 1)
        self.assertEqual(self.folder.getObjectPosition('bar'), 2)

    def testRenameObject(self):
        # Renaming should not change position
        get_transaction().commit(1) # make rename work
        self.folder.manage_renameObjects(['bar'], ['barney'])
        self.assertEqual(self.folder.getObjectPosition('foo'), 0)
        self.assertEqual(self.folder.getObjectPosition('barney'), 1)
        self.assertEqual(self.folder.getObjectPosition('baz'), 2)

    def testRenameFirstObject(self):
        # Renaming should not change position
        get_transaction().commit(1) # make rename work
        self.folder.manage_renameObjects(['foo'], ['flintstone'])
        self.assertEqual(self.folder.getObjectPosition('flintstone'), 0)
        self.assertEqual(self.folder.getObjectPosition('bar'), 1)
        self.assertEqual(self.folder.getObjectPosition('baz'), 2)

    def testRenameLastObject(self):
        # Renaming should not change position
        get_transaction().commit(1) # make rename work
        self.folder.manage_renameObjects(['baz'], ['bedrock'])
        self.assertEqual(self.folder.getObjectPosition('foo'), 0)
        self.assertEqual(self.folder.getObjectPosition('bar'), 1)
        self.assertEqual(self.folder.getObjectPosition('bedrock'), 2)

    def testOrderObjects(self):
        self.folder.orderObjects('id')
        self.assertEqual(self.folder.getObjectPosition('bar'), 0)
        self.assertEqual(self.folder.getObjectPosition('baz'), 1)
        self.assertEqual(self.folder.getObjectPosition('foo'), 2)

    def test_manage_move_objects_up(self):
        # Make sure ZMI method works
        self.folder.manage_move_objects_up(self.app.REQUEST, ids=['bar'])
        self.assertEqual(self.folder.getObjectPosition('bar'), 0)
        self.assertEqual(self.folder.getObjectPosition('foo'), 1)
        self.assertEqual(self.folder.getObjectPosition('baz'), 2)

    def test_manage_move_objects_down(self):
        # Make sure ZMI method works
        self.folder.manage_move_objects_down(self.app.REQUEST, ids=['bar'])
        self.assertEqual(self.folder.getObjectPosition('foo'), 0)
        self.assertEqual(self.folder.getObjectPosition('baz'), 1)
        self.assertEqual(self.folder.getObjectPosition('bar'), 2)

    def test_manage_move_objects_to_top(self):
        # Make sure ZMI method works
        self.folder.manage_move_objects_to_top(self.app.REQUEST, ids=['bar'])
        self.assertEqual(self.folder.getObjectPosition('bar'), 0)
        self.assertEqual(self.folder.getObjectPosition('foo'), 1)
        self.assertEqual(self.folder.getObjectPosition('baz'), 2)

    def test_manage_move_objects_to_bottom(self):
        # Make sure ZMI method works
        self.folder.manage_move_objects_to_bottom(self.app.REQUEST, ids=['bar'])
        self.assertEqual(self.folder.getObjectPosition('foo'), 0)
        self.assertEqual(self.folder.getObjectPosition('baz'), 1)
        self.assertEqual(self.folder.getObjectPosition('bar'), 2)

    def testMoveCMFObjectsOnly(self):
        # Plone speciality
        self.folder.manage_addDTMLMethod('wilma', file='')
        self.assertEqual(self.folder.getObjectPosition('wilma'), 3)
        self.folder.moveObjectToPosition('wilma', 1)
        self.assertEqual(self.folder.getObjectPosition('foo'), 0)
        self.assertEqual(self.folder.getObjectPosition('bar'), 1)
        self.assertEqual(self.folder.getObjectPosition('baz'), 2)
        self.assertEqual(self.folder.getObjectPosition('wilma'), 3) # Did not move

    def testMoveUpCMFObjectsOnly(self):
        # Plone speciality
        self.folder.manage_addDTMLMethod('wilma', file='')
        self.assertEqual(self.folder.getObjectPosition('wilma'), 3)
        self.folder.moveObjectsUp(['baz', 'wilma'])
        self.assertEqual(self.folder.getObjectPosition('foo'), 0)
        self.assertEqual(self.folder.getObjectPosition('baz'), 1) # Moved
        self.assertEqual(self.folder.getObjectPosition('bar'), 2)
        self.assertEqual(self.folder.getObjectPosition('wilma'), 3) # Did not move


class TestOrderSupportInPortal(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.setRoles(['Manager'])
        # Add a bunch of subobjects we can order later on
        self.portal.invokeFactory('Document', id='foo')
        self.portal.invokeFactory('Document', id='bar')
        self.portal.invokeFactory('Document', id='baz')
        # Move them to the top
        from OFS.OrderSupport import OrderSupport
        OrderSupport.moveObjectsByDelta(self.portal, ['foo', 'bar', 'baz'], -len(self.portal._objects))

    def testRenameObject(self):
        # Renaming should not change position
        get_transaction().commit(1) # make rename work
        self.portal.manage_renameObjects(['bar'], ['barney'])
        self.assertEqual(self.portal.getObjectPosition('foo'), 0)
        self.assertEqual(self.portal.getObjectPosition('barney'), 1)
        self.assertEqual(self.portal.getObjectPosition('baz'), 2)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestOrderSupport))
    suite.addTest(makeSuite(TestOrderSupportInPortal))
    return suite

if __name__ == '__main__':
    framework()
