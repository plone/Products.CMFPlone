#
# Tests the content types
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy
from Acquisition import aq_base

from Products.ATContentTypes.interfaces.IATContentType import IATContentType

AddPortalTopics = 'Add portal topics'

atct_types = ('Document', 'Event', 'Favorite', 'File', 'Folder', 
              'Large Plone Folder', 'Image', 'Link', 'News Item',
             )


class TestContentTypes(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        perms = self.getPermissionsOfRole('Member')
        self.setPermissions(perms + [AddPortalTopics], 'Member')
        self.setRoles(['Manager'])
        self.discussion = self.portal.portal_discussion
        self.types = self.portal.portal_types
        self.request = self.app.REQUEST

    def getPermissionsOfRole(self, role):
        perms = self.portal.permissionsOfRole(role)
        return [p['name'] for p in perms if p['selected']]

    def construct(self, portal_type, id, folder):
        fti = self.types.getTypeInfo(portal_type)
        fti.constructInstance(folder, id=id)
        return getattr(folder, id)
    
    def createWithoutConstruction(self, portal_type, id, folder):
        fti = self.types.getTypeInfo(portal_type)
        # manual creation
        p = folder.manage_addProduct[fti.product]
        m = getattr(p, fti.factory)
        m(id) # create it
        return folder._getOb(id)
    
    def testPortalTypeName(self):
        for pt in atct_types:
            ob = self.construct(pt, pt, self.portal)
            self.failUnlessEqual(ob._getPortalTypeName(), pt)
            self.failUnlessEqual(ob.portal_type, pt)
            self.failUnless(IATContentType.isImplementedBy(ob))

    # XXX: disabling as dead Xicken
    def DISABLED_testPortalTypeNameWithoutConstruction(self):
        # Check portal type without using the full constructor
        #
        # Make sure that the portal type is correct inside of mananger_afterAdd
        # and initializeArchetype. There were some problems with LinguaPlone
        # because the portal type name was set *after* object creation and so was
        # wrong inside initializeArchetypes. This has caused some hard to debug
        # errors with workflow states inside of LinguaPlone
        for pt in atct_types:
            ob = self.createWithoutConstruction(pt, pt, self.portal)
            self.failUnlessEqual(ob._getPortalTypeName(), pt)
            # portal_name is different!
            self.failIfEqual(ob.portal_type, pt)
            self.failUnless(ob.portal_type.startswith('AT'))

    def DISABLED_testIndexHtmlIsATCT(self):
        portal = self.portal
        index_html = getattr(aq_base(self), 'index_html', None)
        self.failUnless(IATContentType.isImplementedBy(index_html), index_html.__class__)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestContentTypes))
    return suite

if __name__ == '__main__':
    framework()
