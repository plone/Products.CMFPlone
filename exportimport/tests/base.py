
from Products.GenericSetup.testing import BodyAdapterTestCase
from Products.GenericSetup.testing import NodeAdapterTestCase
from Products.PloneTestCase import layer
from Products.PloneTestCase import setup


# Disable PlacelessSetup as PTC does not like it

class BodyAdapterTestCase(BodyAdapterTestCase):

    if setup.USELAYER:
        layer = layer.ZCML

    def setUp(self):
        pass

    def tearDown(self):
        pass


class NodeAdapterTestCase(NodeAdapterTestCase):

    if setup.USELAYER:
        layer = layer.ZCML

    def setUp(self):
        pass

    def tearDown(self):
        pass

