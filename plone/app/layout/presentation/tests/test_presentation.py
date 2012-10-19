import unittest


class DummyMembershipTool(object):

    def getMemberInfo(self, user_id):
        return {'fullname': 'Test McTester'}


class DummyDocument(object):

    portal_membership = DummyMembershipTool()

    def __init__(self, text, presentation):
        self.text = text
        self.presentation = presentation

    def getPresentation(self):
        return self.presentation

    def CookedBody(self):
        return self.text

    def Creator(self):
        return 'creator'


class TestPresentationView(unittest.TestCase):

    def _makeOne(self, text, presentation):
        doc = DummyDocument(text, presentation)
        from plone.app.layout.presentation.presentation import PresentationView

        from zope.publisher.browser import TestRequest
        request = TestRequest()

        view = PresentationView(doc, request)
        return view

    def test_enabled_h1_turned_on(self):
        view = self._makeOne('<h1>Test</h1><p>Foo</p><h2>foo</h2>', True)
        self.assertTrue(view.enabled())

    def test_enabled_h1_turned_off(self):
        view = self._makeOne('<h1>Test</h1><p>Foo</p><h2>foo</h2>', False)
        self.assertFalse(view.enabled())

    def test_enabled_h2_turned_on(self):
        view = self._makeOne('<h2>Test</h2><p>Foo</p>', True)
        self.assertTrue(view.enabled())

    def test_enabled_h2_turned_off(self):
        view = self._makeOne('<h2>Test</h2><p>Foo</p>', False)
        self.assertFalse(view.enabled())

    def test_enabled_h5_turned_on(self):
        view = self._makeOne('<h5>Bar</h5><p>Foo</p>', True)
        self.assertFalse(view.enabled())

    def test_enabled_h5_turned_off(self):
        view = self._makeOne('<h5>Bar</h5><p>Foo</p>', False)
        self.assertFalse(view.enabled())

    def test_enabled_p_turned_on(self):
        view = self._makeOne('<p>Foo</p>', True)
        self.assertFalse(view.enabled())

    def test_enabled_p_turned_off(self):
        view = self._makeOne('<p>Foo</p>', False)
        self.assertFalse(view.enabled())

    def test_enabled_h1_w_class(self):
        view = self._makeOne('<h1 class="foo">Bar</h1>', True)
        self.assertTrue(view.enabled())

    def test_content_h1(self):
        view = self._makeOne('<h1>Test</h1><p>Foo</p><h2>foo</h2>', True)
        self.assertEqual('<div class="slide">\n<h1>Test</h1><p>Foo</p><h2>foo</h2></div>', view.content())

    def test_content_h1_w_class(self):
        view = self._makeOne('<h1 class="foo">Bar</h1>', True)
        self.assertEqual('<div class="slide">\n<h1 class="foo">Bar</h1></div>', view.content())

    def test_content_h2(self):
        view = self._makeOne('<h2>Test</h2><p>Foo</p>', True)
        self.assertEqual('<div class="slide">\n<h1>Test</h1><p>Foo</p></div>', view.content())
