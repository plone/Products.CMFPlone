from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
import unittest


class DefaultPageTestCase(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'folder', title="Test Folder")
        self.folder = self.portal.folder

    def test_get_default_page_step_1(self):
        # A content object called 'index_html' wins
        self.folder.invokeFactory('Document', 'd1', title="Doc 1")
        self.folder.setDefaultPage('d1')
        self.folder.invokeFactory('Document', 'index_html', title="Doc 2")

        from Products.CMFPlone.defaultpage import get_default_page
        self.assertEqual('index_html', get_default_page(self.folder))

    def test_get_default_page_step_2(self):
        # Else check for IBrowserDefault, either if the container implements
        # it or if an adapter exists. In both cases fetch its FTI and either
        # take it if it implements IDynamicViewTypeInformation or adapt it to
        # IDynamicViewTypeInformation. call get_default_page on the implementer
        # and take value if given.

        # first check some preconditions
        #
        # 1) a folder provides IBrowserDefault
        from Products.CMFDynamicViewFTI.interfaces import IBrowserDefault
        self.assertTrue(IBrowserDefault.providedBy(self.folder))

        # 2) a folder also provides an fti that implements
        #    IDynamicViewTypeInformation
        from Products.CMFDynamicViewFTI.interfaces import IDynamicViewTypeInformation  # noqa
        fti = self.folder.getTypeInfo()
        self.assertTrue(IDynamicViewTypeInformation.providedBy(fti))

        # so if we set a document as defaultpage
        self.folder.invokeFactory('Document', 'd1', title="Doc 1")
        self.folder.setDefaultPage('d1')

        # 3) fti should return it
        self.assertEqual(
            'd1',
            fti.getDefaultPage(self.folder, check_exists=True)
        )

        # now test since we're sure everythings set up correctly
        from Products.CMFPlone.defaultpage import get_default_page
        self.assertEqual('d1', get_default_page(self.folder))

        # missing here:
        # - test adapter instead of direct implements in precondition 1
        # - test adapter instead of direct implements in precondition 2

    def test_get_default_page_step_3_1(self):
        # 3. Else, look up the attribute default_page on the object, without
        #    acquisition in place
        # 3.1 look for a content in the container with the id, no acquisition!
        self.folder.invokeFactory('Document', 'd1', title="Doc 1")
        from Products.CMFPlone.defaultpage import get_default_page

        # set doc d1 must work
        self.folder.default_page = 'd1'
        self.assertEqual('d1', get_default_page(self.folder))

        # set doc d2 must fail and return None
        self.folder.default_page = 'd2'
        self.assertIsNone(get_default_page(self.folder))

        # list of possible values is allowed
        self.folder.default_page = ['d2', 'd1']
        self.assertEqual('d1', get_default_page(self.folder))

        # list of impossible values return None
        self.folder.default_page = ['d2', 'd3']
        self.assertIsNone(get_default_page(self.folder))

        # acquisition check, must not work
        self.folder.invokeFactory('Folder', 'f1', title="Sub Folder 1")
        self.folder.f1.invokeFactory('Document', 'd2', title="Document 2")
        self.folder.default_page = 'd2'
        self.assertIsNone(get_default_page(self.folder.f1))

    def test_get_default_page_step_3_2(self):
        # 3. Else, look up the attribute default_page on the object, without
        #    acquisition in place
        # 3.2 look for a content at portal, with acquisition
        self.portal.invokeFactory('Document', 'd1', title="Doc 1")
        self.folder.default_page = 'd1'
        from Products.CMFPlone.defaultpage import get_default_page

        # now it must acquire from portal
        self.assertEqual('d1', get_default_page(self.folder))

    def test_get_default_page_step_4(self):
        # 4. Else, look up the property default_page in site_properties for
        #   magic ids and test these
        registry = getUtility(IRegistry)
        registry['plone.default_page'] = ['d1']
        self.folder.invokeFactory('Document', 'd1', title="Doc 1")

        from Products.CMFPlone.defaultpage import get_default_page
        self.assertEqual('d1', get_default_page(self.folder))
