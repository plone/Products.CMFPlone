"""Integration tests for the classic portlet type.
"""

import unittest
from Testing.ZopeTestCase import ZopeDocTestSuite

from plone.app.portlets.tests.base import PortletsTestCase
from plone.app.portlets.tests.utils import optionflags

def test_instantiation(self):
    """Ensure a ClassicPortlet can be instantiated
    
    >>> from plone.app.portlets.portlets.classic import ClassicPortletAssignment
    >>> c = ClassicPortletAssignment('template1', 'macro1')
    >>> c.template
    'template1'
    >>> c.macro
    'macro1'
    
    >>> from plone.portlets.interfaces import IPortletDataProvider
    >>> IPortletDataProvider.providedBy(c)
    True
    
    >>> from plone.portlets.interfaces import IPortletAssignment
    >>> IPortletAssignment.providedBy(c)
    True
    """
    
def test_renderer(self):
    """Ensure a ClassicPortlet can be rendered
    
    Create an assignment
    
    >>> from plone.app.portlets.portlets.classic import ClassicPortletAssignment
    >>> a = ClassicPortletAssignment('template1', 'macro1')
    
    Find a portlet context

    >>> from plone.portlets.interfaces import IPortletContext
    >>> portletContext = IPortletContext(self.portal)
    
    Assign the portlet to a manager
    
    >>> from plone.z2.portlets.manager import PortletManager
    >>> m = PortletManager()
    >>> m.setPortletAssignmentsForContext(portletContext.uid, [a])
    
    Find a sample request and view
    
    >>> from zope.publisher.browser import TestRequest
    >>> r = TestRequest()
    
    >>> from Products.CMFPlone.browser.plone import Plone
    >>> v = Plone(self.portal, r)
    
    Find a renderer
    
    >>> from zope.component import getMultiAdapter
    >>> from plone.portlets.interfaces import IPortletRenderer
    
    >>> renderer = getMultiAdapter((self.portal, r, v, m, a.data), IPortletRenderer)
    >>> renderer
    <ClassicPortletRenderer rendering context/template1/macros/macro1>
    
    >>> renderer.use_macro()
    True
    
    >>> renderer.path_expression()
    'context/template1/macros/macro1'
    """
    
def test_renderer_no_macro(self):
    """Ensure a ClassicPortlet can be rendered
    
    Create an assignment
    
    >>> from plone.app.portlets.portlets.classic import ClassicPortletAssignment
    >>> a = ClassicPortletAssignment('template1')
    
    Find a portlet context

    >>> from plone.portlets.interfaces import IPortletContext
    >>> portletContext = IPortletContext(self.portal)
    
    Assign the portlet to a manager
    
    >>> from plone.z2.portlets.manager import PortletManager
    >>> m = PortletManager()
    >>> m.setPortletAssignmentsForContext(portletContext.uid, [a])
    
    Find a sample request and view
    
    >>> from zope.publisher.browser import TestRequest
    >>> r = TestRequest()
    
    >>> from Products.CMFPlone.browser.plone import Plone
    >>> v = Plone(self.portal, r)
    
    Find a renderer
    
    >>> from zope.component import getMultiAdapter
    >>> from plone.portlets.interfaces import IPortletRenderer
    
    >>> renderer = getMultiAdapter((self.portal, r, v, m, a.data), IPortletRenderer)
    >>> renderer
    <ClassicPortletRenderer rendering context/template1>
    
    >>> renderer.use_macro()
    False
    
    >>> renderer.path_expression()
    'context/template1'
    """
    
def test_suite():
    return unittest.TestSuite((
            ZopeDocTestSuite(test_class=PortletsTestCase,
                             optionflags=optionflags),
        ))
