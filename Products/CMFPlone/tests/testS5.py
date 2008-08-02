
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
            view = self.ob.restrictedTraverse("@@presentation_view")
            assert view.enabled() == False
            del self.app.REQUEST.__annotations__
            self.ob.setPresentation(True)
            view = self.ob.restrictedTraverse("@@presentation_view")
            assert view.enabled() == False
            del self.app.REQUEST.__annotations__
            self.ob.setPresentation(False)

    def testHaveHead(self):
        for good in good_ones:
            self.ob.setText(good)
            view = self.ob.restrictedTraverse("@@presentation_view")
            assert view.enabled() == False
            del self.app.REQUEST.__annotations__
            self.ob.setPresentation(True)
            view = self.ob.restrictedTraverse("@@presentation_view")
            assert view.enabled() == True
            del self.app.REQUEST.__annotations__
            self.ob.setPresentation(False)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestS5))
    return suite
