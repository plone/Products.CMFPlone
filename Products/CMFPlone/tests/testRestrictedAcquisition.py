#
# This test module demonstrates a problem caused by the removal of
# a few lines of code from cAccessControl.c and ImplPython.c
# See: http://mail.zope.org/pipermail/zope-checkins/2004-August/028152.html
#
# If an object with setDefaultAccess('deny') is used as the context for
# a PythonScript, the script can no longer acquire tools from the portal
# root. Rolling back the above mentioned checkin restores functionality.
#

from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFPlone.tests import PloneTestCase


class AllowedItem(SimpleItem):
    id = "allowed"
    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")


InitializeClass(AllowedItem)


class DeniedItem(SimpleItem):
    id = "denied"
    security = ClassSecurityInfo()
    security.setDefaultAccess("deny")


InitializeClass(DeniedItem)


class BrokenAcquisitionTest(PloneTestCase.PloneTestCase):
    def afterSetUp(self):
        self.folder = self.portal
        self.folder._setObject("allowed", AllowedItem())
        self.folder._setObject("denied", DeniedItem())

    def _makePS(self, context, id, params, body):
        factory = context.manage_addProduct["PythonScripts"]
        factory.manage_addPythonScript(id)
        ps = context[id]
        ps.ZPythonScript_edit(params, body)

    def testAcquisitionAllowed(self):
        self._makePS(self.folder, "ps", "", "print(context.portal_membership)")
        self.folder.allowed.ps()

    def testAcquisitionDenied(self):
        # This test fails in Zope 2.7.3
        # Also see http://zope.org/Collectors/CMF/259
        self._makePS(self.folder, "ps", "", "print(context.portal_membership)")
        self.folder.denied.ps()
