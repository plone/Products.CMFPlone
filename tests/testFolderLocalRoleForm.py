#
# Tests folder local roles
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.PloneFolder import PloneFolder

class TestFolderLocalRole(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        # The portal has already been set up, so there 
        # is little to do.
        testfolder=PloneFolder('testfolder')
        self.portal._setOb('testfolder',testfolder)
        self.membership=self.portal.portal_membership
        self.membership.addMember('foo','passwd',['Member',],'')
        
    def testAssignUserWithRoles(self):
        """ """
        testfolder=self.portal.testfolder
        testfolder.folder_localrole_edit('add', 'foo', ('Manager',))
        get_transaction().commit()
        foo=self.membership.getMemberById('foo')
        assert 'Manager' in foo.getRolesInContext(testfolder)

    def testRemoveUsersRoles(self):
        testfolder=self.portal.testfolder
        testfolder.folder_localrole_edit('delete', ('Manager',))
        assert 'Manager' not in foo.getRolesInContext(testfolder)

    def testAssignGroupWithRoles(self):
        """ """
        pass

    def testFolderLocalRoleView(self):
        '''folder_localrole_form does not render'''
        self.portal.folder_localrole_form()

            
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestFolderLocalRole))
        return suite

