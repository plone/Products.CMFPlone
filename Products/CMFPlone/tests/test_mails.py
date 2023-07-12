from plone.app.testing import FunctionalTesting
from plone.app.testing import MOCK_MAILHOST_FIXTURE
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.base.interfaces.controlpanel import IMailSchema
from plone.registry.interfaces import IRegistry
from plone.testing import layered
from zope.component import getUtility

import doctest
import re
import unittest


OPTIONFLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE


class MockConfiguredMailHostLayer(PloneSandboxLayer):
    defaultBases = (
        MOCK_MAILHOST_FIXTURE,
        PLONE_FIXTURE,
    )

    def setUpPloneSite(self, portal):
        # We need to fake a valid mail setup:
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        mail_settings.email_from_address = "mail@plone.test"


MOCK_CONFIGURED_MAILHOST_FIXTURE = MockConfiguredMailHostLayer()
MOCK_MAILHOST_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(MOCK_CONFIGURED_MAILHOST_FIXTURE,), name="MockMailHostFixture:Functional"
)


class Py23DocChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        want = re.sub("u'(.*?)'", "'\\1'", want)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def test_suite():
    return unittest.TestSuite(
        (
            layered(
                doctest.DocFileSuite(
                    "mails.txt",
                    optionflags=OPTIONFLAGS,
                    package="Products.CMFPlone.tests",
                    checker=Py23DocChecker(),
                ),
                layer=MOCK_MAILHOST_FUNCTIONAL_TESTING,
            ),
            layered(
                doctest.DocFileSuite(
                    "emaillogin.rst",
                    optionflags=OPTIONFLAGS,
                    package="Products.CMFPlone.tests",
                    checker=Py23DocChecker(),
                ),
                layer=MOCK_MAILHOST_FUNCTIONAL_TESTING,
            ),
        )
    )
