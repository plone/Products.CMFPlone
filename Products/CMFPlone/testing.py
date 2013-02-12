from plone.app.testing import TEST_USER_ID
from plone.app.testing import login
from plone.app.testing import setRoles
import doctest

from zope.configuration import xmlconfig

from plone.testing import z2

from plone.app.testing import PloneSandboxLayer
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting


class ProductsCMFPloneLayer(PloneSandboxLayer):

    def setUpZope(self, app, configurationContext):
        import Products.CMFPlone
        xmlconfig.file(
            'configure.zcml',
            Products.CMFPlone,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        portal.acl_users.userFolderAddUser(
            'admin',
            'secret',
            ['Manager'],
            []
        )
        login(portal, 'admin')
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory(
            "Folder",
            id="test-folder",
            title=u"Test Folder"
        )

    def tearDownPloneSite(self, portal):
        login(portal, 'admin')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.manage_delObjects(['test-folder'])


PRODUCTS_CMFPLONE_FIXTURE = ProductsCMFPloneLayer()

PRODUCTS_CMFPLONE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PRODUCTS_CMFPLONE_FIXTURE,),
    name="CMFPloneLayer:Integration"
)
PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PRODUCTS_CMFPLONE_FIXTURE,),
    name="CMFPloneLayer:Functional"
)
PRODUCTS_CMFPLONE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(PRODUCTS_CMFPLONE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="CMFPloneLayer:Acceptance"
)

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
