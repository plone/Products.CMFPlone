
from Products.GenericSetup.testing import BodyAdapterTestCase
from Products.GenericSetup.testing import NodeAdapterTestCase


# Disable PlacelessSetup as PTC does not like it

class BodyAdapterTestCase(BodyAdapterTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass


class NodeAdapterTestCase(NodeAdapterTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

