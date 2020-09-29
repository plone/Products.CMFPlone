from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING  # noqa
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from plone.testing import layered

import doctest
import glob
import os
import re
import unittest


UNITTESTS = ['messages.txt', 'mails.txt', 'emaillogin.rst', 'translate.txt']
CONTENT_TESTS = [
    'AddMoveAndDeleteDocument.txt',
    'base_tag_not_present.txt',
    'browser.txt',
    'browser_collection_views.txt',
    'csrf.txt',
    'link_redirect_view.txt',
]
OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


class Py23DocChecker(doctest.OutputChecker):

    def check_output(self, want, got, optionflags):
        # translate doctest exceptions
        # TODO: fix tests to check for full path
        for dotted in ('urllib.error.HTTPError', ):
            if dotted in got:
                got = re.sub(
                    dotted,
                    dotted.rpartition('.')[-1],
                    got,
                )

        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def test_suite():
    # Some files need to be tested with the standard functional layer.
    ignored = UNITTESTS + CONTENT_TESTS
    standard_filenames = [
        filename for filename in
        glob.glob(os.path.sep.join([os.path.dirname(__file__), '*.txt']))
        if os.path.basename(filename) not in ignored
    ]
    suites = [
        layered(
            doctest.DocFileSuite(
                os.path.basename(filename),
                optionflags=OPTIONFLAGS,
                package='Products.CMFPlone.tests',
                checker=Py23DocChecker(),
            ),
            layer=PLONE_FUNCTIONAL_TESTING
        ) for filename in standard_filenames
    ]

    # Other files need to be tested with the plone.app.contenttypes layer.
    content_filenames = [
        filename for filename in
        glob.glob(os.path.sep.join([os.path.dirname(__file__), '*.txt']))
        if os.path.basename(filename) in CONTENT_TESTS
    ]
    suites.extend([
        layered(
            doctest.DocFileSuite(
                os.path.basename(filename),
                optionflags=OPTIONFLAGS,
                package='Products.CMFPlone.tests',
                checker=Py23DocChecker(),
            ),
            layer=PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING
        ) for filename in content_filenames
    ])

    return unittest.TestSuite(suites)
