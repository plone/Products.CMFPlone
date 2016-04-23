# -*- coding: utf-8 -*-
from zope.interface import Attribute
from zope.interface import Interface

import doctest
import unittest


optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS

# Used in tests


class IZero(Interface):
    ''' Test interface zero
    '''


class IOne(IZero):
    ''' Test interface one
    '''
    one_name = Attribute('One name for IOne')

    def one_function():
        '''One function for IOne'''


class ITwo(Interface):
    ''' Test interface two
    '''
    pass


class NotAnInterface(object):
    pass


def test_interface_view(self):
    """Information about the interfaces of an object

    >>> from zope.interface import Interface, implements
    >>> from zope.interface import directlyProvides, classProvides
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
    >>> provideAdapter(
    ...    InterfaceInformation,
    ...    (Interface, IBrowserRequest),
    ...    Interface, u'plone_interface_info'
    ... )

    >>> obj = One()
    >>> request = TestRequest()

    >>> directlyProvides(request, IAttributeAnnotatable)
    >>> view = getMultiAdapter((obj, request), name=u'plone_interface_info')

    >>> view.provides('plone.app.layout.globals.tests.test_interface.IOne')
    True
    >>> view.provides('plone.app.layout.globals.tests.test_interface.ITwo')
    False
    >>> view.provides(
    ...     'plone.app.layout.globals.tests.test_interface.NotAnInterface')
    Traceback (most recent call last):
    ...
    ValueError: \
'plone.app.layout.globals.tests.test_interface.NotAnInterface' \
is not a valid Interface.

    >>> view.class_provides(
    ...     'plone.app.layout.globals.tests.test_interface.IOne')
    False
    >>> view.class_provides(
    ...     'plone.app.layout.globals.tests.test_interface.ITwo')
    True
    >>> view.class_provides(
    ...     'plone.app.layout.globals.tests.test_interface.NotAnInterface')
    Traceback (most recent call last):
    ...
    ValueError: \
'plone.app.layout.globals.tests.test_interface.NotAnInterface' \
is not a valid Interface.

    >>> view.names_and_descriptions(
    ...     'plone.app.layout.globals.tests.test_interface.IOne')[0]
    ('one_function', 'One function for IOne')
    >>> view.names_and_descriptions(
    ...     'plone.app.layout.globals.tests.test_interface.IOne')[1]
    ('one_name', 'One name for IOne')

    >>> view.get_base_interface()
    []
    >>> iface_info = view.get_interface_informations(IOne)
    >>> iface_info['dotted_name']
    'plone.app.layout.globals.tests.test_interface.IOne'
    >>> iface_info['name']
    'IOne'
    >>> iface_info['doc']
    'One name for IOne'
    >>> iface_info['bases']
    [<InterfaceClass plone.app.layout.globals.tests.test_interface.IZero>]
    >>> iface_info['base_names']
    ['plone.app.layout.globals.tests.test_interface.IOne']
    >>> iface_info['attributes'][0]['doc']
    'One name for IOne'
    >>> iface_info['attributes'][0]['name']
    'one_name'
    >>> iface_info['methods'][0]['doc']
    'One function for IOne'
    >>> iface_info['methods'][0]['name']
    'one_function'
    >>> iface_info['methods'][0]['signature']
    '()'
    """


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(optionflags=optionflags))
    return suite
