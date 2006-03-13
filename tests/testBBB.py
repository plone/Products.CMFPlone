import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Setup the monkeys
from Products.CMFPlone import bbb

import unittest

from zope.component import queryMultiAdapter
from zope.component import getMultiAdapter
from zope.component.exceptions import ComponentLookupError

from zope.interface import Interface
from zope.interface import implements
from zope.interface.verify import verifyObject
from zope.app.tests import placelesssetup
from zope.app.tests import ztapi

ZOPE28 = True
try:
    from zope.component.tests.request import Request
    from zope.component import getService
    from zope.component.servicenames import Adapters
    from zope.component.servicenames import Presentation
except ImportError:
    ZOPE28 = False

# Copied from zope.component.tests.test_api to test that getMultiadapter works
# as expected and handles all view lookup responsibilities
test_entries = []

Test = object()

class I1(Interface):
    pass
class I2(Interface):
    pass
class I3(Interface):
    pass

class Comp(object):
    implements(I2)
    def __init__(self, context, request=None):
        self.context = context

class DoubleAdapter(object):
    implements(I3)
    def __init__(self, first, second):
        self.first = first
        self.second = second

class Ob(object):
    implements(I1)

ob = Ob()

class Ob2(object):
    implements(I2)


class TestZope28BBB(unittest.TestCase):
    """Tests to ensure that the BBB queryMultiadapter for 2.8 looks up
       both multiadapters and views, as in 2.9"""

    def testQueryMultiAdapter(self):
        # Adapting a combination of 2 objects to an interface
        ob2 = Ob2()
        context = None
        ztapi.provideAdapter([I1, I2], I3, DoubleAdapter, '')
        c = queryMultiAdapter((ob, ob2), I3, context=context)
        self.assertEquals(c.__class__, DoubleAdapter)
        self.assertEquals(c.first, ob)
        self.assertEquals(c.second, ob2)

    def testMyBlahBlah(self):
        self.assertEquals(queryMultiAdapter((ob, Request(I2)), name='foo', default=Test), Test)

        ztapi.provideView(I1, I2, Interface, 'foo', Comp)
        c = getMultiAdapter((ob, Request(I2)), name='foo')
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

        self.assertRaises(ComponentLookupError,
                          getMultiAdapter, (ob, Request(I1)), name='foo2')
        self.assertRaises(ComponentLookupError,
                          getMultiAdapter, (ob, Request(I2)), name='foo2')
        self.assertEquals(queryMultiAdapter((ob, Request(I2)), name='foo2',
                                             default=Test), Test)

        self.assertEquals(queryMultiAdapter((ob, Request(I1)), name='foo2',
                                             default=None), None)

    def testView_w_provided(self):
        self.assertRaises(ComponentLookupError,
                          getMultiAdapter, (ob, Request(I2)),
                                            interface=I3, name='foo')
        self.assertRaises(ComponentLookupError,
                          getMultiAdapter, (ob, Request(I2)),
                                            interface=I3, name='foo')
        self.assertEquals(
            queryMultiAdapter((ob, Request(I2)), interface=I3,
                               name='foo', default=Test), Test)

        ztapi.provideView(I1, I2, Interface, 'foo', Comp)

        self.assertRaises(ComponentLookupError,
                          getMultiAdapter, (ob, Request(I1)),
                                            interface=I3, name='foo')
        self.assertRaises(ComponentLookupError,
                          getMultiAdapter, (ob, Request(I2)),
                                            interface=I3, name='foo')
        self.assertEquals(
            queryMultiAdapter((ob, Request(I2)), interface=I3,
                               name='foo', default=Test), Test)

        ztapi.provideView(I1, I2, I3, 'foo', Comp)

        c = getMultiAdapter((ob, Request(I2)), interface=I3, name='foo')
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

        c = getMultiAdapter((ob, Request(I2)), name='foo')
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

if ZOPE28:
    test_entries.append(TestZope28BBB)

def test_suite():
    suite = unittest.TestSuite()
    for elem in test_entries:
        suite.addTest(unittest.makeSuite(elem))
    return suite

if __name__ == "__main__":
    placelesssetup.setUp()
    unittest.TextTestRunner().run(test_suite())
    placelesssetup.tearDown()