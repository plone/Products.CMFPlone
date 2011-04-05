import unittest

from Products.GenericSetup.testing import BodyAdapterTestCase
from Products.GenericSetup.testing import NodeAdapterTestCase
from Products.PloneTestCase import layer
from Products.PloneTestCase import setup


class BodyAdapterTestCase(BodyAdapterTestCase, unittest.TestCase):

    if setup.USELAYER:
        layer = layer.ZCML

    def setUp(self):
        pass

    def tearDown(self):
        pass


class NodeAdapterTestCase(NodeAdapterTestCase, unittest.TestCase):

    if setup.USELAYER:
        layer = layer.ZCML

    def setUp(self):
        pass

    def tearDown(self):
        pass
