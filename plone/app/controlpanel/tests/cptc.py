"""Base class for control panel test cases.

This is in a separate module because it's potentially useful to other
packages which register controlpanels. They should be able to import it
without the PloneTestCase.setupPloneSite() side effects.
"""

from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.Five.testbrowser import Browser
from Products.CMFCore.utils import getToolByName

class ControlPanelTestCase(FunctionalTestCase):
    """base test case with convenience methods for all control panel tests"""
    
    def afterSetUp(self):
        super(ControlPanelTestCase, self).afterSetUp()
        
        self.browser = Browser()
        
        self.uf = self.portal.acl_users
        self.uf.userFolderAddUser('root', 'secret', ['Manager'], [])
        
        self.ptool = getToolByName(self.portal, 'portal_properties')
        self.site_props = self.ptool.site_properties
    
    def loginAsManager(self, user='root', pwd='secret'):
        """points the browser to the login screen and logs in as user root with Manager role."""
        self.browser.open('http://nohost/plone/')
        self.browser.getLink('Log in').click()
        self.browser.getControl('Login Name').value = user
        self.browser.getControl('Password').value = pwd
        self.browser.getControl('Log in').click()

class UserGroupsControlPanelTestCase(ControlPanelTestCase):
    """user/groups-specific test case"""

    def afterSetUp(self):
        super(UserGroupsControlPanelTestCase, self).afterSetUp()
        self.generateUsers()
        self.generateGroups()

    def generateGroups(self):
        groupsTool = getToolByName(self.portal, 'portal_groups')
        groupsTool.addGroup('Foo', [], [], {'title': 'Foo'})
        
    def generateUsers(self):
        members = [{'username': 'DIispfuF', 'fullname': 'Kevin Hughes', 'email': 'DIispfuF@foo.com'}, 
                   {'username': 'enTHXigm', 'fullname': 'Richard Ramirez', 'email': 'enTHXigm@foo.com'}, 
                   {'username': 'q7UsYcrT', 'fullname': 'Kyle Brown', 'email': 'q7UsYcrT@foo.com'}, 
                   {'username': 'j5g0xPmr', 'fullname': 'Julian Green', 'email': 'j5g0xPmr@foo.com'}, 
                   {'username': 'o6Sx4It3', 'fullname': 'Makayla Coleman', 'email': 'o6Sx4It3@foo.com'}, 
                   {'username': 'SLUhquYa', 'fullname': 'Sean Foster', 'email': 'SLUhquYa@foo.com'}, 
                   {'username': 'nHWl3Ita', 'fullname': 'Molly Martin', 'email': 'nHWl3Ita@foo.com'}, 
                   {'username': 'xdkpCKmX', 'fullname': 'Jordan Thompson', 'email': 'xdkpCKmX@foo.com'}, 
                   {'username': 'p8H6CicB', 'fullname': 'Tyler Rivera', 'email': 'p8H6CicB@foo.com'}, 
                   {'username': 'T6vdBXbD', 'fullname': 'Megan Murphy', 'email': 'T6vdBXbD@foo.com'}, 
                   {'username': 'DohPmgIa', 'fullname': 'Gracie Diaz', 'email': 'DohPmgIa@foo.com'}, 
                   {'username': 'CqHWi65B', 'fullname': 'Rachel Morgan', 'email': 'CqHWi65B@foo.com'}, 
                   {'username': 'uHFQ7qk4', 'fullname': 'Maya Price', 'email': 'uHFQ7qk4@foo.com'}, 
                   {'username': 'BlXLQh7r', 'fullname': 'Blake Jenkins', 'email': 'BlXLQh7r@foo.com'}, 
                   {'username': 'FCrWUiSY', 'fullname': 'Owen Ramirez', 'email': 'FCrWUiSY@foo.com'}, 
                   {'username': 'bX3PqgHK', 'fullname': 'Owen Cook', 'email': 'bX3PqgHK@foo.com'}, 
                   {'username': 'sD35vVl0', 'fullname': 'Jayden Hill', 'email': 'sD35vVl0@foo.com'}, 
                   {'username': 'mfOcjXAG', 'fullname': 'Joseph Ramirez', 'email': 'mfOcjXAG@foo.com'}, 
                   {'username': 'GAJtdYbM', 'fullname': 'Nathan Young', 'email': 'GAJtdYbM@foo.com'}, 
                   {'username': 'E1OWG6bv', 'fullname': 'Kaitlyn Hernandez', 'email': 'E1OWG6bv@foo.com'}, 
                   {'username': 'BqOX2sCm', 'fullname': 'Faith Price', 'email': 'BqOX2sCm@foo.com'}, 
                   {'username': 'tyOxRnml', 'fullname': 'Sofia Williams', 'email': '5yOxRjtl@foo.com'}, 
                   {'username': 'fVcumDNl', 'fullname': 'David Sanders', 'email': 'fVcumDNl@foo.com'}, 
                   {'username': 'Ge1hqdEI', 'fullname': 'Jack Simmons', 'email': 'Ge1hqdEI@foo.com'}, 
                   {'username': 'o2CqT7kG', 'fullname': 'Cole Howard', 'email': 'o2CqT7kG@foo.com'}, 
                   {'username': 'mpGtfNl6', 'fullname': 'Rachel Miller', 'email': 'mpGtfNl6@foo.com'}, 
                   {'username': 'RGrpWiBg', 'fullname': 'Henry Patterson', 'email': 'RGrpWiBg@foo.com'}, 
                   {'username': 'Bufmi0YS', 'fullname': 'Avery Cooper', 'email': 'Bufmi0YS@foo.com'}, 
                   {'username': 'J7NvbjYd', 'fullname': 'Sydney Bennett', 'email': 'J7NvbjYd@foo.com'}, 
                   {'username': 'u5Xem8U1', 'fullname': 'Daniel Johnson', 'email': 'u5Xem8U1@foo.com'}, 
                   {'username': 'TWrMCLIo', 'fullname': 'Autumn Brooks', 'email': '0VrMCLIo@foo.com'}, 
                   {'username': 'FElYwiIr', 'fullname': 'Alexandra Nelson', 'email': 'FElYwiIr@foo.com'}, 
                   {'username': 'teK6pkhc', 'fullname': 'Brian Simmons', 'email': '0eK6pkhc@foo.com'}, 
                   {'username': 'RwAO2YPa', 'fullname': 'Gracie Adams', 'email': 'gracie@foo.com'}, 
                   {'username': 'nlBMw26i', 'fullname': 'Sydney Evans', 'email': 'nlBMw26i@foo.com'}, 
                   {'username': 'Ahr3EiRC', 'fullname': 'Emma Brown', 'email': 'Ahr3EiRC@foo.com'}, 
                   {'username': 'NP4FMIb5', 'fullname': 'Jesus Hayes', 'email': 'NP4FMIb5@foo.com'}, 
                   {'username': 'NhuU0Y5x', 'fullname': 'Lauren Martin', 'email': 'NhuU0Y5x@foo.com'}, 
                   {'username': 'j2R3mKQg', 'fullname': 'Isabelle Russell', 'email': 'j2R3mKQg@foo.com'}, 
                   {'username': 'qOmK0iCN', 'fullname': 'Anna Baker', 'email': 'qOmK0iCN@foo.com'}, 
                   {'username': 'uQbVOgo7', 'fullname': 'Brady Watson', 'email': 'uQbVOgo7@foo.com'}, 
                   {'username': 'oLDCaQfW', 'fullname': 'Kaitlyn Robinson', 'email': 'oLDCaQfW@foo.com'}, 
                   {'username': 'osYHeFD1', 'fullname': 'Riley Richardson', 'email': 'osYHeFD1@foo.com'}, 
                   {'username': 'i4pHduDY', 'fullname': 'Kayla Sanders', 'email': 'i4pHduDY@foo.com'}, 
                   {'username': 'BvyX6qF3', 'fullname': 'Sara Richardson', 'email': 'BvyX6qF3@foo.com'}, 
                   {'username': 'a3EpwDYj', 'fullname': 'Trinity Gonzales', 'email': 'a3EpwDYj@foo.com'}, 
                   {'username': 'JDMseWdt', 'fullname': 'Madeline Garcia', 'email': 'JDMseWdt@foo.com'}, 
                   {'username': 'lPCYBvoi', 'fullname': 'Brian Gray', 'email': 'lPCYBvoi@foo.com'}, 
                   {'username': 'AByCsRQ3', 'fullname': 'Victoria Perez', 'email': 'AByCsRQ3@foo.com'}, 
                   {'username': 'CH7uVlNy', 'fullname': 'Charles Rodriguez', 'email': '5H7uVlNy@foo.com'}, 
                   {'username': 'XYsmd7ux', 'fullname': 'Abigail Simmons', 'email': 'XYsmd7ux@foo.com'}]
        regtool = getToolByName(self.portal, 'portal_registration')
        for member in members:
            regtool.addMember(member['username'], 'somepassword', properties=member)
        