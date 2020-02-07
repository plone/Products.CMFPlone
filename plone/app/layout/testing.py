# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from Products.CMFPlone.utils import _createObjectByType


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.layout

        self.loadZCML(package=plone.app.layout)

    def setUpPloneSite(self, portal):
        _createObjectByType("Folder", portal, id="Members")
        mtool = portal.portal_membership
        if not mtool.getMemberareaCreationFlag():
            mtool.setMemberareaCreationFlag()
        mtool.createMemberArea(TEST_USER_ID)
        if mtool.getMemberareaCreationFlag():
            mtool.setMemberareaCreationFlag()


FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="plone.app.layout:Integration",
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="plone.app.layout:Functional",
)
