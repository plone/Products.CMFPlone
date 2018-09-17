# -*- coding: utf-8 -*-
from plone.app.layout.testing import INTEGRATION_TESTING
from plone.app.layout.testing import FUNCTIONAL_TESTING
from plone.app.layout.testing import TEST_USER_ID

import unittest


class ViewletsTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        self.folder = self.portal['Members'][TEST_USER_ID]


class ViewletsFunctionalTestCase(unittest.TestCase):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        self.folder = self.portal['Members'][TEST_USER_ID]
