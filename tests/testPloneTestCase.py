#
# Example PloneTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase


class TestPloneTestCase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow

    def testAddDocument(self):
        assert not self.catalog(id='new')
        self.folder.invokeFactory('Document', id='new')
        assert hasattr(self.folder.aq_base, 'new')
        assert self.catalog(id='new')

    def testPublishDocument(self):
        self.folder.invokeFactory('Document', id='new')
        assert self.workflow.getInfoFor(self.folder.new, 'review_state') == 'visible'
        assert not self.catalog(id='new', review_state='published')
        self.setRoles(['Reviewer'])
        self.workflow.doActionFor(self.folder.new, 'publish')
        assert self.workflow.getInfoFor(self.folder.new, 'review_state') == 'published'
        assert self.catalog(id='new', review_state='published')

    def testRetractDocument(self):
        self.folder.invokeFactory('Document', id='new')
        self.setRoles(['Reviewer'])
        self.workflow.doActionFor(self.folder.new, 'publish')
        assert self.workflow.getInfoFor(self.folder.new, 'review_state') == 'published'
        self.setRoles(['Member'])
        self.workflow.doActionFor(self.folder.new, 'retract')
        assert self.workflow.getInfoFor(self.folder.new, 'review_state') == 'visible'

    def testGetterSkinScript(self):
        self.folder.invokeFactory('Document', id='new', title='foo')
        assert self.folder.new.TitleOrId() == 'foo'

    def testSetterSkinScript(self):
        self.folder.invokeFactory('Document', id='new')
        assert self.folder.new.EditableBody() == ''
        self.folder.new.document_edit('plain', 'data')
        assert self.folder.new.EditableBody() == 'data'                                                         
            
    def testEditDocument(self):
        self.folder.invokeFactory('Document', id='new')
        assert self.folder.new.EditableBody() == ''
        self.folder.new.edit('plain', 'data', file='', safety_belt='')
        assert self.folder.new.EditableBody() == 'data'


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestPloneTestCase))
        return suite

