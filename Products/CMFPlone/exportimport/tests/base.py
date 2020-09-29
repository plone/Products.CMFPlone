from plone.testing.zca import UNIT_TESTING
from Products.GenericSetup.testing import BodyAdapterTestCase
from Products.GenericSetup.testing import NodeAdapterTestCase
import unittest


class BodyAdapterTestCase(BodyAdapterTestCase, unittest.TestCase):

    layer = UNIT_TESTING


class NodeAdapterTestCase(NodeAdapterTestCase, unittest.TestCase):

    layer = UNIT_TESTING
