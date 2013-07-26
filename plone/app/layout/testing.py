# -*- coding: utf-8 -*-

from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.layout
        self.loadZCML(package=plone.app.layout)

FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='plone.app.layout:Integration',
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='plone.app.layout:Functional',
)
