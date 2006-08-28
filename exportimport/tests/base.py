
from Products.GenericSetup.testing import BodyAdapterTestCase
from Products.GenericSetup.testing import NodeAdapterTestCase
from Products.PloneTestCase.layer import ZCMLLayer


# Disable PlacelessSetup as PTC does not like it

class BodyAdapterTestCase(BodyAdapterTestCase):

    layer = ZCMLLayer

    def setUp(self):
        pass

    def tearDown(self):
        pass


class NodeAdapterTestCase(NodeAdapterTestCase):

    layer = ZCMLLayer

    def setUp(self):
        pass

    def tearDown(self):
        pass

