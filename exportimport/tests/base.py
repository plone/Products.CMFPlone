
from Products.GenericSetup.testing import BodyAdapterTestCase
from Products.GenericSetup.testing import NodeAdapterTestCase
from Products.PloneTestCase.layer import ZCMLLayer
import Products.PloneTestCase.setup as setup

# Disable PlacelessSetup as PTC does not like it

class BodyAdapterTestCase(BodyAdapterTestCase):

    if setup.USELAYER:
        layer = ZCMLLayer

    def setUp(self):
        pass

    def tearDown(self):
        pass


class NodeAdapterTestCase(NodeAdapterTestCase):

    if setup.USELAYER:
        layer = ZCMLLayer

    def setUp(self):
        pass

    def tearDown(self):
        pass

