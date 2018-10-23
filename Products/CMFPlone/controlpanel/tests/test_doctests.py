# -*- coding: utf-8 -*-
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from plone.testing import layered

import doctest
import re
import six
import unittest


class Py23DocChecker(doctest.OutputChecker):

    def check_output(self, want, got, optionflags):
        if not six.PY2:
            want = re.sub("u'(.*?)'", "'\\1'", want)
            want = re.sub('u"(.*?)"', '"\\1"', want)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


tests = ('../README.rst',)


def test_suite():
    return unittest.TestSuite(
        [
            layered(
                doctest.DocFileSuite(
                    f,
                    optionflags=doctest.ELLIPSIS,
                    checker=Py23DocChecker(),
                ),
                layer=PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
            )
            for f in tests
        ]
    )
