import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFPlone.tests import PloneTestCase

import transaction

bad_ones = [
    "<p>Foo</p>",
    "<h5>Bar</h5><p>Foo</p>",    
    ]
good_ones = [
    "<h2>Test</h2><p>Foo</p>",
    "<h1>Test</h1><p>Foo</p><h2>foo</h2><p>bar</p>",    
    ]


class TestS5(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.folder.invokeFactory('Document', id='foo')
        self.ob = self.folder.restrictedTraverse('foo')

    def testNoHead(self):
        for bad in bad_ones:
            self.ob.setText(bad)
            self.assertRaises(ValueError, self.ob.document_s5_alter)
            assert self.ob.document_s5_alter(test=True) == False
            self.ob.setPresentation(True)
            self.assertRaises(ValueError, self.ob.document_s5_alter)
            assert self.ob.document_s5_alter(test=True) == False
            self.ob.setPresentation(False)
            
    def testHaveHead(self):
        for good in good_ones:
            self.ob.setText(good)
            self.assertRaises(ValueError, self.ob.document_s5_alter)
            assert self.ob.document_s5_alter(test=True) == False
            self.ob.setPresentation(True)
            self.ob.document_s5_alter()
            assert self.ob.document_s5_alter(test=True) == True
            self.ob.setPresentation(False)
            

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestS5))
    return suite

if __name__ == '__main__':
    framework()
