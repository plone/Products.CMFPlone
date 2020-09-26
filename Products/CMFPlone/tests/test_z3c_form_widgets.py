from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from z3c.form import widget
from z3c.form.browser.text import TextWidget

import unittest


WIDGETS_TO_TEST = [
    TextWidget,
    widget.Widget,
    widget.MultiWidget,
    widget.SequenceWidget,
]

_marker = object()


class FakeForm:
    method = 'post'
    ignoreRequest = False


class TestAttackVector(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
    _widgets_to_test = WIDGETS_TO_TEST
    _attack = '</textarea><script>alert("form.widgets")</script>'  # noqa

    def _terms(self):
        # For the SequenceWidget we need basic terms.
        # We make dummy (dumb) terms.
        from z3c.form.term import Terms

        class DummyTerms(Terms):
            def getTermByToken(self, token):
                return token

        return DummyTerms()

    def test_regression(self):
        request = self.layer['request']
        for Widget in self._widgets_to_test:
            wi = Widget(request)
            wi.name = 'foo'
            request.REQUEST_METHOD = 'POST'
            request.form.update({
                'foo': 'bar'
            })
            wi.form = FakeForm()
            self.assertEqual(wi.ignoreRequest, False)
            # The SequenceWidget needs terms.  It will have terms=None,
            # where the others have no terms attribute.
            if getattr(wi, 'terms', _marker) is None:
                wi.terms = self._terms()
            wi.update()
            self.assertEqual(wi.ignoreRequest, False)

    def test_only_get_data_from_valid_request_method(self):
        request = self.layer['request']
        for Widget in self._widgets_to_test:
            wi = Widget(request)
            wi.name = 'foobar'
            request.REQUEST_METHOD = 'GET'
            request.form.update({
                'foobar': self._attack
            })
            wi.form = FakeForm()
            self.assertEqual(wi.ignoreRequest, False)
            # The SequenceWidget needs terms.  It will have terms=None,
            # where the others have no terms attribute.
            if getattr(wi, 'terms', _marker) is None:
                wi.terms = self._terms()
            wi.update()
            self.assertEqual(wi.ignoreRequest, True)

    def test_explicitly_allow_data_from_invalid_request_method(self):
        request = self.layer['request']
        for Widget in self._widgets_to_test:
            wi = Widget(request)
            wi.name = 'foobar'
            request.REQUEST_METHOD = 'GET'
            request.form.update({
                'foobar': self._attack
            })
            wi.form = FakeForm()
            # Set attribute on form to explicitly allow prefill.
            from Products.CMFPlone.patches.z3c_form import ALLOW_PREFILL
            setattr(wi.form, ALLOW_PREFILL, True)
            self.assertEqual(wi.ignoreRequest, False)
            # The SequenceWidget needs terms.  It will have terms=None,
            # where the others have no terms attribute.
            if getattr(wi, 'terms', _marker) is None:
                wi.terms = self._terms()
            wi.update()
            self.assertEqual(wi.ignoreRequest, False)

    def test_only_get_data_from_valid_referrer(self):
        # this handles the use case where hijacker gets user to click on
        # button that submits to plone site
        request = self.layer['request']

        for Widget in self._widgets_to_test:
            wi = Widget(request)
            wi.name = 'foobar'
            request.REQUEST_METHOD = 'POST'
            request.form.update({
                'foobar': self._attack
            })
            request.environ['HTTP_REFERER'] = 'http://attacker.com'
            wi.form = FakeForm()
            self.assertEqual(wi.ignoreRequest, False)
            # The SequenceWidget needs terms.  It will have terms=None,
            # where the others have no terms attribute.
            if getattr(wi, 'terms', _marker) is None:
                wi.terms = self._terms()
            wi.update()
            self.assertEqual(wi.ignoreRequest, True)
