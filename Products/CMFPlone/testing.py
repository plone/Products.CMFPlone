from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework import AutoLogin
from plone.app.robotframework import Content
from plone.app.robotframework import RemoteLibraryLayer
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting
from plone.testing import z2
from Products.CMFPlone.tests.robot.robot_setup import CMFPloneRemoteKeywords
from zope.configuration import xmlconfig
import doctest


class ProductsCMFPloneLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

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
        # XXX: this is needed for tests that rely on the Members folder to be
        # present. This folder is otherwise created by a setup handler in
        # ATContentTypes, but that package is optional now.
        if 'Members' not in portal.keys():
            portal.invokeFactory(
                "Folder",
                id="Members",
                title=u"Members"
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

PRODUCTS_CMFPLONE_ROBOT_REMOTE_LIBRARY_FIXTURE = RemoteLibraryLayer(
    bases=(
        PLONE_FIXTURE,
    ),
    libraries=(AutoLogin, Content, CMFPloneRemoteKeywords),
    name="CMFPloneRobotRemoteLibrary:RobotRemote"
)

PRODUCTS_CMFPLONE_ROBOT_TESTING = FunctionalTesting(
    bases=(
        PRODUCTS_CMFPLONE_FIXTURE,
        PRODUCTS_CMFPLONE_ROBOT_REMOTE_LIBRARY_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name="CMFPloneLayer:Acceptance"
)

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
