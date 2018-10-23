# -*- coding: utf-8 -*-
from unittest import TestSuite

import doctest
import re
import six


class Py23DocChecker(doctest.OutputChecker):

    def check_output(self, want, got, optionflags):
        if not six.PY2:
            want = re.sub("u'(.*?)'", "'\\1'", want)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def test_suite():
    suites = (
        doctest.DocFileSuite(
            'messages.txt',
            package='Products.CMFPlone.tests',
            checker=Py23DocChecker(),
            ),
        doctest.DocTestSuite('Products.CMFPlone.i18nl10n'),
        doctest.DocTestSuite('Products.CMFPlone.TranslationServiceTool'),
        doctest.DocTestSuite('Products.CMFPlone.utils'),
        doctest.DocTestSuite('Products.CMFPlone.workflow'),
    )

    return TestSuite(suites)
