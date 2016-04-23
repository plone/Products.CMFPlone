# -*- coding: utf-8 -*-
from plone.app.layout.testing import INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import unittest


class DefaultPageTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'folder', title=u"Test Folder")
        self.folder = self.portal.folder

    def test_getDefaultPage_step_1(self):
        # A content object called 'index_html' wins
        self.folder.invokeFactory('Document', 'd1', title=u"Doc 1")
        self.folder.setDefaultPage('d1')
        self.folder.invokeFactory('Document', 'index_html', title=u"Doc 2")

        from plone.app.layout.navigation.defaultpage import getDefaultPage
        self.assertEqual('index_html', getDefaultPage(self.folder))

    def test_getDefaultPage_step_2(self):
        # Else check for IBrowserDefault, either if the container implements
        # it or if an adapter exists. In both cases fetch its FTI and either
        # take it if it implements IDynamicViewTypeInformation or adapt it to
        # IDynamicViewTypeInformation. call getDefaultPage on the implementer
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
        self.folder.invokeFactory('Document', 'd1', title=u"Doc 1")
        self.folder.setDefaultPage('d1')

        # 3) fti should return it
        self.assertEqual(
            'd1',
            fti.getDefaultPage(self.folder, check_exists=True)
        )

        # now test since we're sure everythings set up correctly
        from plone.app.layout.navigation.defaultpage import getDefaultPage
        self.assertEqual('d1', getDefaultPage(self.folder))

        # missing here:
        # - test adapter instead of direct implements in precondition 1
        # - test adapter instead of direct implements in precondition 2

    def test_getDefaultPage_step_3_1(self):
        # 3. Else, look up the attribute default_page on the object, without
        #    acquisition in place
        # 3.1 look for a content in the container with the id, no acquisition!
        self.folder.invokeFactory('Document', 'd1', title=u"Doc 1")
        from plone.app.layout.navigation.defaultpage import getDefaultPage

        # set doc d1 must work
        self.folder.default_page = 'd1'
        self.assertEqual('d1', getDefaultPage(self.folder))

        # set doc d2 must fail and return None
        self.folder.default_page = 'd2'
        self.assertIsNone(getDefaultPage(self.folder))

        # list of possible values is allowed
        self.folder.default_page = ['d2', 'd1']
        self.assertEqual('d1', getDefaultPage(self.folder))

        # list of impossible values return None
        self.folder.default_page = ['d2', 'd3']
        self.assertIsNone(getDefaultPage(self.folder))

        # acquisition check, must not work
        self.folder.invokeFactory('Folder', 'f1', title=u"Sub Folder 1")
        self.folder.f1.invokeFactory('Document', 'd2', title=u"Document 2")
        self.folder.default_page = 'd2'
        self.assertIsNone(getDefaultPage(self.folder.f1))

    def test_getDefaultPage_step_3_2(self):
        # 3. Else, look up the attribute default_page on the object, without
        #    acquisition in place
        # 3.2 look for a content at portal, with acquisition
        self.portal.invokeFactory('Document', 'd1', title=u"Doc 1")
        self.folder.default_page = 'd1'
        from plone.app.layout.navigation.defaultpage import getDefaultPage

        # now it must acquire from portal
        self.assertEqual('d1', getDefaultPage(self.folder))

        # fetch from i.e. portal_skins by acquisition
        # test_rendering.pt is in portal_skins/plone_templates and so available
        # by acquisition
        self.folder.default_page = 'test_rendering'
        self.assertEqual('test_rendering', getDefaultPage(self.folder))

    def test_getDefaultPage_step_4(self):
        # 4. Else, look up the property default_page in the configuration
        # registry for magic ids and test these
        registry = getUtility(IRegistry)
        registry['plone.default_page'] = [u'd1']
        self.folder.invokeFactory('Document', 'd1', title=u"Doc 1")

        from plone.app.layout.navigation.defaultpage import getDefaultPage
        self.assertEqual('d1', getDefaultPage(self.folder))
