#
# Tests for prepare_slots functionality
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFPlone.tests import PloneTestCase

from Products.CMFPlone.browser.plone import Plone

class TestPrepareSlots(PloneTestCase.PloneTestCase):

    def addPS(self, id, params='', body=''):
        self.folder.manage_addProduct['PythonScripts'].manage_addPythonScript(id)
        self.folder[id].ZPythonScript_edit(params, body)

    def addPT(self, id, title='', text=''):
        self.folder.manage_addProduct['PageTemplates'].manage_addPageTemplate(id, title, text)

    def testDefaultSlots(self):
        view = Plone(self.folder, self.app.REQUEST)
        slots = view._prepare_slots()
        self.failUnless(len(slots['left']) > 0)
        self.assertEqual(len(slots['right']), 0)

    def testAcquiredFromPortal(self):
        pslots = self.portal.Members.prepare_slots()
        fslots = self.folder.prepare_slots()
        self.assertEqual(fslots['left'], pslots['left'])
        # right slots are intercepted by Members folder
        self.assertEqual(fslots['document_actions'], pslots['document_actions'])

    def testAcquiredFromMembers(self):
        mslots = self.portal.Members.prepare_slots()
        fslots = self.folder.prepare_slots()
        self.assertEqual(fslots['left'], mslots['left'])
        self.assertEqual(fslots['right'], mslots['right'])
        self.assertEqual(fslots['document_actions'], mslots['document_actions'])

    def testFolderPropertyOverridesLeftSlots(self):
        self.folder.manage_addProperty('left_slots', ['foo'], 'lines')
        slots = self.folder.prepare_slots()
        self.assertEqual(slots['left'], [('foo', 0)])

    def testFolderPropertyOverridesRightSlots(self):
        self.folder.manage_addProperty('right_slots', ['foo'], 'lines')
        slots = self.folder.prepare_slots()
        self.assertEqual(slots['right'], [('foo', 0)])

    def testFolderPropertyOverridesDocumentActionSlots(self):
        self.folder.manage_addProperty('document_action_slots', ['foo'], 'lines')
        slots = self.folder.prepare_slots()
        self.assertEqual(slots['document_actions'], [('foo', 0)])

    def testTemplatePropertyOverridesLeftSlots(self):
        self.addPT('pt')
        self.folder.pt.manage_addProperty('left_slots', ['foo'], 'lines')
        slots = self.folder.pt.prepare_slots()
        self.assertEqual(slots['left'], [('foo', 0)])

    def testTemplatePropertyOverridesRightSlots(self):
        self.addPT('pt')
        self.folder.pt.manage_addProperty('right_slots', ['foo'], 'lines')
        slots = self.folder.pt.prepare_slots()
        self.assertEqual(slots['right'], [('foo', 0)])

    def testTemplatePropertyOverridesDocumentActionSlots(self):
        self.addPT('pt')
        self.folder.pt.manage_addProperty('document_action_slots', ['foo'], 'lines')
        slots = self.folder.pt.prepare_slots()
        self.assertEqual(slots['document_actions'], [('foo', 0)])

    def testScriptOverridesLeftSlots(self):
        self.setRoles(['Manager'])
        self.addPS('left_slots', body="return ['foo']")
        slots = self.folder.prepare_slots()
        self.assertEqual(slots['left'], [('foo', 0)])

    def testScriptOverridesRightSlots(self):
        self.setRoles(['Manager'])
        self.addPS('right_slots', body="return ['foo']")
        slots = self.folder.prepare_slots()
        self.assertEqual(slots['right'], [('foo', 0)])

    def testScriptOverridesDocumentActionSlots(self):
        self.setRoles(['Manager'])
        self.addPS('document_action_slots', body="return ['foo']")
        slots = self.folder.prepare_slots()
        self.assertEqual(slots['document_actions'], [('foo', 0)])

    def testMethodOverridesLeftSlots(self):
        def leftSlots(): return ['foo']
        self.folder.left_slots = leftSlots
        slots = self.folder.prepare_slots()
        self.assertEqual(slots['left'], [('foo', 0)])

    def testMethodOverridesRightSlots(self):
        def rightSlots(): return ['foo']
        self.folder.right_slots = rightSlots
        slots = self.folder.prepare_slots()
        self.assertEqual(slots['right'], [('foo', 0)])

    def testMethodOverridesDocumentActionSlots(self):
        def documentActionSlots(): return ['foo']
        self.folder.document_action_slots = documentActionSlots
        slots = self.folder.prepare_slots()
        self.assertEqual(slots['document_actions'], [('foo', 0)])

    def testLeftSlotsMacro(self):
        def leftSlots(): return ['/macros/foo']
        self.folder.left_slots = leftSlots
        slots = self.folder.prepare_slots()
        self.assertEqual(slots['left'], [('/macros/foo', 1)])

    def testRightSlotsMacro(self):
        def rightSlots(): return ['/macros/foo']
        self.folder.right_slots = rightSlots
        slots = self.folder.prepare_slots()
        self.assertEqual(slots['right'], [('/macros/foo', 1)])

    def testDocumentActionSlotsMacro(self):
        def documentActionSlots(): return ['/macros/foo']
        self.folder.document_action_slots = documentActionSlots
        slots = self.folder.prepare_slots()
        self.assertEqual(slots['document_actions'], [('/macros/foo', 1)])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPrepareSlots))
    return suite

if __name__ == '__main__':
    framework()
