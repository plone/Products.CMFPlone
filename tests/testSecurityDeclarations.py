#
# Tests the security declarations Plone makes on resources 
# for access by restricted code (aka PythonScripts)
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

from OFS.SimpleItem import SimpleItem
from AccessControl import Unauthorized
from ZODB.POSException import ConflictError
from Products.ZCTextIndex.ParseTree import ParseError
from OFS.CopySupport import CopyError
from Products.CMFDefault.DiscussionTool import DiscussionNotAllowed


class RestrictedPythonTest(ZopeTestCase.ZopeTestCase):

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

    def checkUnauthorized(self, psbody):
        self.addPS('ps', body=psbody)
        try:
            self.folder.ps()
        except (AttributeError, ImportError, Unauthorized):
            pass


class TestSecurityDeclarations(RestrictedPythonTest):

    # NOTE: This test case is a bit hairy. Security declarations
    # "stick" once a module has been imported into the restricted
    # environment. Therefore the tests are not truly independent.
    # Be careful when adding new tests to this class.

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

    def testImport_WARNING(self):
        self.check('from zLOG import WARNING')

    def testAccess_WARNING(self):
        self.check('import zLOG;'
                   'print zLOG.WARNING')

    def testImport_getLogger(self):
        self.check('from logging import getLogger')

    def testAccess_getLogger(self):
        self.check('from logging import getLogger;'
                   'log = getLogger("testlog");'
                   'log.debug("test")')

    def testImport_IndexIterator(self):
        self.check('from Products.CMFPlone import IndexIterator')

    def testAccess_IndexIterator(self):
        self.check('from Products import CMFPlone;'
                   'print CMFPlone.IndexIterator')

    def testUse_IndexIterator(self):
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

    def testImport_base_hasattr(self):
        self.check('from Products.CMFPlone import base_hasattr')

    def testAccess_base_hasattr(self):
        self.check('import Products.CMFPlone;'
                   'print Products.CMFPlone.base_hasattr')

    def testImport_shasattr(self):
        self.check('from Products.CMFPlone import shasattr')

    def testAccess_shasattr(self):
        self.check('import Products.CMFPlone;'
                   'print Products.CMFPlone.shasattr')

    def testImport_safe_callable(self):
        self.check('from Products.CMFPlone import safe_callable')

    def testAccess_safe_callable(self):
        self.check('import Products.CMFPlone;'
                   'print Products.CMFPlone.safe_callable')

    def testImport_Unauthorized(self):
        self.check('from AccessControl import Unauthorized')

    def testAccess_Unauthorized(self):
        self.check('import AccessControl;'
                   'print AccessControl.Unauthorized')

    def testImport_zExceptionsUnauthorized(self):
        # XXX: Note that this is not allowed
        self.checkUnauthorized('from zExceptions import Unauthorized')

    def testImport_ConflictError(self):
        self.check('from ZODB.POSException import ConflictError')

    def testAccess_ConflictError(self):
        self.check('import ZODB.POSException;'
                   'print ZODB.POSException.ConflictError')

    def testRaise_ConflictError(self):
        self.assertRaises(ConflictError, 
            self.check, 'from ZODB.POSException import ConflictError;'
                        'raise ConflictError')

    def testCatch_ConflictErrorRaisedByRestrictedCode(self):
        try:
            self.check('''
from ZODB.POSException import ConflictError
try: raise ConflictError
except ConflictError: pass
''')
        except Exception, e:
            self.fail('Failed to catch: %s %s (module %s)' %
                      (e.__class__.__name__, e, e.__module__))

    def testCatch_ConflictErrorRaisedByPythonModule(self):
        self.folder._setObject('raiseConflictError', dummy.Raiser(ConflictError))
        try:
            self.check('''
from ZODB.POSException import ConflictError
try: context.raiseConflictError()
except ConflictError: pass
''')
        except Exception, e:
            self.fail('Failed to catch: %s %s (module %s)' %
                      (e.__class__.__name__, e, e.__module__))

    def testImport_getToolByName(self):
        self.check('from Products.CMFCore.utils import getToolByName')

    def testAccess_getToolByName(self):
        # XXX: Note that this is NOT allowed!
        self.checkUnauthorized('from Products.CMFCore import utils;'
                               'print utils.getToolByName')

    def testUse_getToolByName(self):
        self.app.manage_addFolder('portal_membership') # Fake a portal tool
        self.check('from Products.CMFCore.utils import getToolByName;'
                   'print getToolByName(context, "portal_membership")')

    def testImport_ParseError(self):
        self.check('from Products.ZCTextIndex.ParseTree import ParseError')

    def testAccess_ParseError(self):
        self.check('import Products.ZCTextIndex.ParseTree;'
                   'print Products.ZCTextIndex.ParseTree.ParseError')

    def testCatch_ParseErrorRaisedByPythonModule(self):
        self.folder._setObject('raiseParseError', dummy.Raiser(ParseError))
        try:
            self.check('''
from Products.ZCTextIndex.ParseTree import ParseError
try: context.raiseParseError()
except ParseError: pass
''')
        except Exception, e:
            self.fail('Failed to catch: %s %s (module %s)' %
                      (e.__class__.__name__, e, e.__module__))

    try:
        from DateTime.DateTime import DateTimeError
    except ImportError:
        pass
    else:
        def testImport_DateTimeError(self):
            self.check('from DateTime.DateTime import DateTimeError')

        def testAccess_DateTimeError(self):
            self.check('import DateTime.DateTime;'
                       'print DateTime.DateTime.DateTimeError')

        def testCatch_DateTimeErrorRaisedByPythonModule(self):
            self.folder._setObject('raiseDateTimeError', dummy.Raiser(self.DateTimeError))
            try:
                self.check('''
from DateTime.DateTime import DateTimeError
try: context.raiseDateTimeError()
except DateTimeError: pass
''')
            except Exception, e:
                self.fail('Failed to catch: %s %s (module %s)' %
                          (e.__class__.__name__, e, e.__module__))

    try:
        from DateTime.DateTime import SyntaxError
    except ImportError:
        pass
    else:
        def testImport_SyntaxError(self):
            self.check('from DateTime.DateTime import SyntaxError')

        def testAccess_SyntaxError(self):
            self.check('import DateTime.DateTime;'
                       'print DateTime.DateTime.SyntaxError')

        def testCatch_SyntaxErrorRaisedByPythonModule(self):
            self.folder._setObject('raiseSyntaxError', dummy.Raiser(self.SyntaxError))
            try:
                self.check('''
from DateTime.DateTime import SyntaxError
try: context.raiseSyntaxError()
except SyntaxError: pass
''')
            except Exception, e:
                self.fail('Failed to catch: %s %s (module %s)' %
                          (e.__class__.__name__, e, e.__module__))

    try:
        from Products import PlacelessTranslationService
    except ImportError:
        pass
    else:
        def testImport_PTS(self):
            self.check('from Products import PlacelessTranslationService')

        def testImport_isRTL(self):
            self.check('from Products.PlacelessTranslationService import isRTL')

        def testAccess_isRTL(self):
            self.check('import Products.PlacelessTranslationService;'
                       'print Products.PlacelessTranslationService.isRTL')

    def testImport_CopyError(self):
        self.check('from OFS.CopySupport import CopyError')

    def testAccess_CopyError(self):
        self.check('import OFS.CopySupport;'
                   'print OFS.CopySupport.CopyError')

    def testCatch_CopyErrorRaisedByPythonModule(self):
        self.folder._setObject('raiseCopyError', dummy.Raiser(CopyError))
        try:
            self.check('''
from OFS.CopySupport import CopyError
try: context.raiseCopyError()
except CopyError: pass
''')
        except Exception, e:
            self.fail('Failed to catch: %s %s (module %s)' %
                      (e.__class__.__name__, e, e.__module__))

    def testImport_DiscussionNotAllowed(self):
        self.check('from Products.CMFDefault.DiscussionTool '
                   'import DiscussionNotAllowed')

    def testAccess_DiscussionNotAllowed(self):
        self.check('import Products.CMFDefault.DiscussionTool;'
                   'print Products.CMFDefault.DiscussionTool.DiscussionNotAllowed')

    def testCatch_DiscussionNotAllowedRaisedByPythonModule(self):
        self.folder._setObject('raiseDiscussionNotAllowed',
                               dummy.Raiser(DiscussionNotAllowed))
        try:
            self.check('''
from Products.CMFDefault.DiscussionTool import DiscussionNotAllowed
try: context.raiseDiscussionNotAllowed()
except DiscussionNotAllowed: pass
''')
        except Exception, e:
            self.fail('Failed to catch: %s %s (module %s)' %
                      (e.__class__.__name__, e, e.__module__))


class TestAcquisitionMethods(RestrictedPythonTest):

    def test_aq_explicit(self):
        self.check('print context.aq_explicit')

    def test_aq_parent(self):
        self.check('print context.aq_parent')

    def test_aq_inner(self):
        self.check('print context.aq_inner')

    def test_aq_inner_aq_parent(self):
        self.check('print context.aq_inner.aq_parent')

    def test_aq_self(self):
        self.checkUnauthorized('print context.aq_self')

    def test_aq_base(self):
        self.checkUnauthorized('print context.aq_base')

    def test_aq_acquire(self):
        self.checkUnauthorized('print context.aq_acquire')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSecurityDeclarations))
    suite.addTest(makeSuite(TestAcquisitionMethods))
    return suite

if __name__ == '__main__':
    framework()
