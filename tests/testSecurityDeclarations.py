#
# Tests the security declarations Plone makes on resources 
# for access by restricted code (aka PythonScripts)
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from AccessControl import Unauthorized


class TestSecurityDeclarations(PloneTestCase.PloneTestCase):

    # NOTE: This testcase is a bit hairy. Security declarations
    # "stick" once a module has been imported into the restricted
    # environment. Therefore the tests are not truly independent.
    # Be careful when adding new tests to this class.

    def addPS(self, id, params='', body=''):
        factory = self.folder.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript(id)
        self.folder[id].ZPythonScript_edit(params, body)

    def check(self, psbody):
        self.addPS('ps', body=psbody)
        try: 
            self.folder.ps()
        except (ImportError, Unauthorized), e:
            self.fail(e)

    def testImport_LOG(self):
        self.check('from zLOG import LOG')

    def testAccess_LOG(self):
        self.check('import zLOG;' 
                   'print zLOG.LOG')

    def testImport_INFO(self):
        self.check('from zLOG import INFO')

    def testAccess_INFO(self):
        self.check('import zLOG;'
                   'print zLOG.INFO')

    def testImport_translate_wrapper(self):
        self.check('from Products.CMFPlone.PloneUtilities import translate_wrapper')
        
    def testAccess_translate_wrapper(self):
        self.check('import Products.CMFPlone.PloneUtilities;'
                   'print Products.CMFPlone.PloneUtilities.translate_wrapper')

    def testImport_localized_time(self):
        self.check('from Products.CMFPlone.PloneUtilities import localized_time')

    def testAccess_localized_time(self):
        self.check('import Products.CMFPlone.PloneUtilities;'
                   'print Products.CMFPlone.PloneUtilities.localized_time')

    def testImport_IndexIterator(self):
        self.check('from Products.CMFPlone import IndexIterator')

    def testAccess_IndexIterator(self):
        self.check('from Products import CMFPlone;'
                   'print CMFPlone.IndexIterator')

    def testUseClass_IndexIterator(self):
        self.check('from Products.CMFPlone import IndexIterator;'
                   'print IndexIterator().next')

    def testImport_ObjectMoved(self):
        self.check('from Products.CMFCore.WorkflowCore import ObjectMoved')

    def testAccess_ObjectMoved(self):
        self.check('from Products.CMFCore import WorkflowCore;'
                   'print WorkflowCore.ObjectMoved')

    def testUse_ObjectMoved(self):
        self.check('from Products.CMFCore.WorkflowCore import ObjectMoved;'
                   'print ObjectMoved("foo").getResult')

    def testImport_ObjectDeleted(self):
        self.check('from Products.CMFCore.WorkflowCore import ObjectDeleted')

    def testAccess_ObjectDeleted(self):
        self.check('from Products.CMFCore import WorkflowCore;'
                   'print WorkflowCore.ObjectDeleted')

    def testUse_ObjectDeleted(self):
        self.check('from Products.CMFCore.WorkflowCore import ObjectDeleted;'
                   'print ObjectDeleted().getResult')

    def testImport_WorkflowException(self):
        self.check('from Products.CMFCore.WorkflowCore import WorkflowException')

    def testAccess_WorkflowException(self):
        self.check('from Products.CMFCore import WorkflowCore;'
                   'print WorkflowCore.WorkflowException')

    def testUse_WorkflowException(self):
        self.check('from Products.CMFCore.WorkflowCore import WorkflowException;'
                   'print WorkflowException().args')

    def testImport_Batch(self):
        self.check('from Products.CMFPlone import Batch')

    def testAccess_Batch(self):
        self.check('from Products import CMFPlone;'
                   'print CMFPlone.Batch')

    def testUse_Batch(self):
        self.check('from Products.CMFPlone import Batch;'
                   'print Batch([], 0).nexturls')

    def testImport_transaction_note(self):
        self.check('from Products.CMFPlone import transaction_note')

    def testAccess_transaction_note(self):
        self.check('import Products.CMFPlone;'
                   'print Products.CMFPlone.transaction_note')

    def testImport_listPolicies(self):
        self.check('from Products.CMFPlone.Portal import listPolicies')

    def testAccess_listPolicies(self):
        self.check('import Products.CMFPlone.Portal;'
                   'print Products.CMFPlone.Portal.listPolicies')

    def testImport_Unauthorized(self):
        self.check('from AccessControl import Unauthorized')

    def testAccess_Unauthorized(self):
        self.check('import AccessControl;'
                   'print AccessControl.Unauthorized')

    def testImport_ConflictError(self):
        self.check('from ZODB.POSException import ConflictError')

    def testAccess_ConflictError(self):
        self.check('import ZODB.POSException;'
                   'print ZODB.POSException.ConflictError')

    def testImport_base_hasattr(self):
        self.check('from Products.CMFPlone import base_hasattr')

    def testAccess_base_hasattr(self):
        self.check('import Products.CMFPlone;'
                   'print Products.CMFPlone.base_hasattr')


if __name__ == '__main__':
    framework()
else:
    def test_suite():
        from unittest import TestSuite, makeSuite
        suite = TestSuite()
        suite.addTest(makeSuite(TestSecurityDeclarations))
        return suite
