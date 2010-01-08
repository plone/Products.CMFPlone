import unittest
import doctest

from plone.app.portlets.tests.base import PortletsTestCase

from Testing import ZopeTestCase as ztc

def test_suite():

    import plone.app.portlets.storage

    return unittest.TestSuite([

        ztc.ZopeDocTestSuite(
            module=plone.app.portlets.storage,
            test_class=PortletsTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        ])
