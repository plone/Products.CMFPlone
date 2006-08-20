"""Integration tests for adapter registrations.

These tests ensure that the various adapter registrations are in effect,
not the exact functionality they promise. They utilise the full PloneTestCase
bases, since we are actually testing that the registrations are properly loaded
at Zope start-up, not just that they could be made to work (e.g. using the
zope testing API)
"""

import unittest
from Testing.ZopeTestCase import ZopeDocTestSuite

from plone.app.portlets.tests.base import PortletsTestCase
from plone.app.portlets.tests.utils import optionflags

def test_default_adapter():
    """Test the default portlet context adapter
    
    >>> from plone.portlets.interfaces import IPortletContext
    >>> folderContext = IPortletContext(self.folder)
    
    On Archetypes objects, the UID is the AT UID. The parent lookup uses 
    acquisition.
    
    >>> folderContext.uid == self.folder.UID()
    True
    >>> folderContext.parent is self.folder.aq_parent
    True
    
    The userId property should return the current user's id.
    
    >>> from Testing.ZopeTestCase import user_name
    >>> folderContext.userId == user_name
    True
    
    The groupIds property should return a list of group ids.
    
    >>> tuple(folderContext.groupIds)
    ()
    
    >>> group = self.portal.portal_groups.getGroupById('Reviewers')
    >>> self.setRoles(('Manager',))
    >>> group.addMember(user_name)
    >>> self.setRoles(('Member',))
    >>> tuple(folderContext.groupIds)
    ('Reviewers',)
    
    The context should also work for the anonymous user.
    
    >>> self.logout()
    
    >>> folderContext.uid == self.folder.UID()
    True
    >>> folderContext.parent == self.folder.aq_parent
    True
    
    >>> folderContext.userId == None
    True
    >>> folderContext.groupIds
    ()
    """
    
def test_default_adapter_non_archetypes():
    """For a type not providing IReferenceable, the path will be used as the
    UID.
    
    >>> from Products.CMFPlone.utils import _createObjectByType
    >>> obj = _createObjectByType('CMF Folder', self.folder, 'cmffolder')
    
    >>> from plone.portlets.interfaces import IPortletContext
    >>> folderContext = IPortletContext(self.folder.cmffolder)
    >>> folderContext.uid == '/'.join(self.folder.cmffolder.getPhysicalPath())
    True
    """
    
def test_portal_root_adapter():
    """The portal root version of the adapter always has parent = None
    
    >>> from plone.portlets.interfaces import IPortletContext
    >>> portalContext = IPortletContext(self.portal)
    >>> portalContext.parent == None
    True
    """
    
def test_suite():
    return unittest.TestSuite((
            ZopeDocTestSuite(test_class=PortletsTestCase,
                             optionflags=optionflags),
        ))
