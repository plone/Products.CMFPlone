#
# test the related items support
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.Archetypes.tests.test_baseschema import BaseSchemaTest
from Products.Archetypes.tests.utils import makeContent


class TestRelatedItems(BaseSchemaTest):

    def testRelatedItems(self):
        obj1 = makeContent( self.folder,    
                    id="obj1",
                    portal_type="Document",
                    title='Obj1')
        obj2 = makeContent( self.folder,
                    id="obj2",
                    portal_type="Document",
                    title='Obj2')

        obj1.setRelatedItems([obj2.UID()])

        # call the script for retrieving the items
        l = obj1.computeRelatedItems()

        # check length
        self.assertEqual(len(l),1)

        # check object
        self.assertEqual(l[0],obj2)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRelatedItems))
    return suite

if __name__ == '__main__':
    framework()
