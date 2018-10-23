# -*- coding: utf-8 -*-
import unittest
from Products.CMFPlone.tests import PloneTestCase

try:
    import Products.ExternalEditor
except ImportError:
    HAS_EXTERNAL_EDITOR = False
else:
    HAS_EXTERNAL_EDITOR = True


@unittest.skipIf(not HAS_EXTERNAL_EDITOR, 'requires Products.ExternalEditor')
class TestExternalEditorEnabled(PloneTestCase.PloneTestCase):
    '''Tests the externalEditorEnabled script'''

    def afterSetUp(self):
        PloneTestCase.PloneTestCase.afterSetUp(self)
        self.folder.invokeFactory('Document', 'doc')
        self.doc = self.folder.doc
        self.folder.invokeFactory('Folder', 'folder2')
        self.folder = self.folder.folder2
        self.portal.acl_users._doAddUser('user1', 'secret', ['Member'], [])
        self.mtool = self.portal.portal_membership
        member = self.mtool.getAuthenticatedMember()
        member.setMemberProperties({'ext_editor': 1})

        self.lockbody = ('<?xml version="1.0" encoding="utf-8"?>\n'
                         '<d:lockinfo xmlns:d="DAV:">\n'
                         '  <d:lockscope><d:exclusive/></d:lockscope>\n'
                         '  <d:locktype><d:write/></d:locktype>\n'
                         '  <d:depth>infinity</d:depth>\n'
                         '  <d:owner>\n'
                         '  <d:href>Zope External Editor</d:href>\n'
                         '  </d:owner>\n'
                         '</d:lockinfo>'
                         )

    def testFailForAnonymous(self):
        self.assertTrue(self.doc.externalEditorEnabled())
        self.logout()
        self.assertFalse(self.doc.externalEditorEnabled())

    def testFailOnDisabledMemberProperty(self):
        self.assertTrue(self.doc.externalEditorEnabled())
        member = self.mtool.getAuthenticatedMember()
        member.setMemberProperties({'ext_editor': 0})
        self.assertFalse(self.doc.externalEditorEnabled())

    def testFailOnUnSupportedObjects(self):
        # Structural Folders are not editable by default
        self.assertFalse(self.folder.externalEditorEnabled())

    def testFailWithoutUseExtEditPermission(self):
        self.portal.manage_permission('Use external editor',
                                      ('Owner', 'Manager'), 0)
        self.login('user1')
        self.assertFalse(self.doc.externalEditorEnabled())

    def testFailWhenObjectIsLocked(self):
        # Should not show if someone already has a webdav lock on the object
        self.doc.REQUEST.set('BODY', self.lockbody)
        self.doc.LOCK(self.doc.REQUEST, self.doc.REQUEST.RESPONSE)
        self.assertFalse(self.doc.externalEditorEnabled())
        self.doc.wl_clearLocks()
        self.assertTrue(self.doc.externalEditorEnabled())

    def testExternalEditorUsesZemExtensionForOSX(self):
        self.doc.external_edit()
        redirect = self.doc.REQUEST.RESPONSE.headers['location']
        self.assertTrue(redirect.endswith('doc'))

        # if Mac OS X in the user agent, add a .zem extension
        self.doc.REQUEST.environ['HTTP_USER_AGENT'] = 'Mac OS X'
        self.doc.external_edit()
        redirect = self.doc.REQUEST.RESPONSE.headers['location']
        self.assertTrue(redirect.endswith('.zem?macosx=1'))
