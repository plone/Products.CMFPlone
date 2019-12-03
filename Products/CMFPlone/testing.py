from plone.app.testing import TEST_USER_ID
from plone.app.testing import login
from plone.app.testing import setRoles
import doctest

from zope.configuration import xmlconfig

from plone.testing import z2

from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting

from plone.app.robotframework import RemoteLibraryLayer
from plone.app.robotframework import AutoLogin

from Products.CMFPlone.tests.robot.robot_setup import CMFPloneRemoteKeywords


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


class UnstyledThemeLayer(ProductsCMFPloneLayer):

    def setUpPloneSite(self, portal):
        super(UnstyledThemeLayer, self).setUpPloneSite(portal)
        portal.portal_skins.default_skin = 'Plone Default'


class ClassicThemeLayer(ProductsCMFPloneLayer):

    def setUpZope(self, app, configurationContext):
        super(ClassicThemeLayer, self).setUpZope(app, configurationContext)
        import plonetheme.classic
        xmlconfig.file(
            'configure.zcml',
            plonetheme.classic,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        super(ClassicThemeLayer, self).setUpPloneSite(portal)
        portal.portal_quickinstaller.installProducts(['plonetheme.classic'])
        portal.portal_skins.default_skin = 'Plone Classic Theme'


PRODUCTS_CMFPLONE_FIXTURE = ProductsCMFPloneLayer()
UNSTYLED_THEME_FIXTURE = UnstyledThemeLayer()
CLASSIC_THEME_FIXTURE = ClassicThemeLayer()

PRODUCTS_CMFPLONE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PRODUCTS_CMFPLONE_FIXTURE,),
    name="CMFPloneLayer:Integration"
)
PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PRODUCTS_CMFPLONE_FIXTURE,),
    name="CMFPloneLayer:Functional"
)

PRODUCTS_CMFPLONE_ROBOT_REMOTE_LIBRARY_FIXTURE = RemoteLibraryLayer(
    bases=(PLONE_FIXTURE,),
    libraries=(AutoLogin, CMFPloneRemoteKeywords),
    name="CMFPloneRobotRemoteLibrary:RobotRemote"
)

PRODUCTS_CMFPLONE_ROBOT_TESTING = FunctionalTesting(
    bases=(PRODUCTS_CMFPLONE_FIXTURE,
           PRODUCTS_CMFPLONE_ROBOT_REMOTE_LIBRARY_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name="CMFPloneLayer:Acceptance"
)

UNSTYLED_THEME_ROBOT_TESTING = FunctionalTesting(
    bases=(UNSTYLED_THEME_FIXTURE,
           PRODUCTS_CMFPLONE_ROBOT_REMOTE_LIBRARY_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name="UnstyledThemingLayer:Acceptance"
)

CLASSIC_THEME_ROBOT_TESTING = FunctionalTesting(
    bases=(CLASSIC_THEME_FIXTURE,
           PRODUCTS_CMFPLONE_ROBOT_REMOTE_LIBRARY_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name="ClassicThemingLayer:Acceptance"
)

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
