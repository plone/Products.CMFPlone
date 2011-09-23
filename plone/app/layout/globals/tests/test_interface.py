import unittest
import doctest

optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS

# Used in tests

from zope.interface import Interface

class IOne(Interface):
    pass

class ITwo(Interface):
    pass

class NotAnInterface(object):
    pass

def test_interface_view(self):
    """Information about the interfaces of an object

    >>> from zope.interface import Interface, implements, directlyProvides, classProvides
    >>> from zope.component import provideAdapter, getMultiAdapter
    >>> from zope.publisher.interfaces.browser import IBrowserRequest
    >>> from zope.publisher.browser import TestRequest

    >>> from zope.annotation.interfaces import IAttributeAnnotatable
    >>> from zope.annotation.attribute import AttributeAnnotations
    >>> provideAdapter(AttributeAnnotations)

    >>> from plone.app.layout.globals.tests.test_interface import IOne, ITwo

    >>> class One(object):
    ...     implements(IOne)
    ...     classProvides(ITwo)

    >>> from plone.app.layout.globals.interface import InterfaceInformation
    >>> provideAdapter(InterfaceInformation, (Interface, IBrowserRequest), Interface, u'plone_interface_info')

    >>> obj = One()
    >>> request = TestRequest()

    >>> directlyProvides(request, IAttributeAnnotatable)
    >>> view = getMultiAdapter((obj, request), name=u'plone_interface_info')

    >>> view.provides('plone.app.layout.globals.tests.test_interface.IOne')
    True
    >>> view.provides('plone.app.layout.globals.tests.test_interface.ITwo')
    False
    >>> view.provides('plone.app.layout.globals.tests.test_interface.NotAnInterface')
    Traceback (most recent call last):
    ...
    ValueError: 'plone.app.layout.globals.tests.test_interface.NotAnInterface' is not a valid Interface.

    >>> view.class_provides('plone.app.layout.globals.tests.test_interface.IOne')
    False
    >>> view.class_provides('plone.app.layout.globals.tests.test_interface.ITwo')
    True
    >>> view.class_provides('plone.app.layout.globals.tests.test_interface.NotAnInterface')
    Traceback (most recent call last):
    ...
    ValueError: 'plone.app.layout.globals.tests.test_interface.NotAnInterface' is not a valid Interface.
    """

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(optionflags=optionflags))
    return suite
