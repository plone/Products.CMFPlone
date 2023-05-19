from AccessControl import Unauthorized
from plone.app.testing.bbb import PloneTestCase
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.tests import dummy
from Products.CMFPlone.utils import check_id
from ZODB.POSException import ConflictError


class TestCheckId(PloneTestCase):
    def testGoodId(self):
        r = check_id(self.folder, "foo")
        self.assertEqual(r, None)  # success

    def testEmptyId(self):
        r = check_id(self.folder, "")
        self.assertEqual(r, None)  # success

    def testRequiredId(self):
        r = check_id(self.folder, "", required=1)
        self.assertEqual(r, "Please enter a name.")

    def testAlternativeId(self):
        r = check_id(self.folder, "", alternative_id="foo")
        self.assertEqual(r, None)  # success

    def testBadId(self):
        # See https://github.com/zopefoundation/Zope/pull/181
        r = check_id(self.folder, "=")
        self.assertEqual(r, None)

    def testDecodeId(self):
        # See https://github.com/zopefoundation/Zope/pull/181
        r = check_id(self.folder, "\xc3\xa4")
        self.assertEqual(r, None)

    def testCatalogIndex(self):
        # TODO: Tripwire
        portal_membership = getToolByName(self.portal, "portal_membership")
        have_permission = portal_membership.checkPermission
        self.assertTrue(
            have_permission("Search ZCatalog", self.portal.portal_catalog),
            'Expected permission "Search ZCatalog"',
        )

        r = check_id(self.folder, "created")
        self.assertEqual(r, "created is reserved.")

    def testCatalogMetadata(self):
        portal_catalog = getToolByName(self.portal, "portal_catalog")
        portal_catalog.addColumn("new_metadata")
        self.assertTrue("new_metadata" in portal_catalog.schema())
        self.assertFalse("new_metadata" in portal_catalog.indexes())
        r = check_id(self.folder, "new_metadata")
        self.assertEqual(r, "new_metadata is reserved.")

    def testCollision(self):
        self.folder.invokeFactory("Document", id="foo")
        self.folder.invokeFactory("Document", id="bar")
        r = check_id(self.folder.foo, "bar")
        self.assertEqual(r, "There is already an item named bar in this " "folder.")

    def testReservedId(self):
        self.folder._setObject("foo", dummy.Item("foo"))
        r = check_id(self.folder.foo, "portal_catalog")
        self.assertEqual(r, "portal_catalog is reserved.")

    def testHiddenObjectId(self):
        # If a parallel object is not in content-space, should get 'reserved'
        # instead of 'taken'
        r = check_id(self.folder, "portal_skins")
        self.assertEqual(r, "portal_skins is reserved.")

    def testCanOverrideParentNames(self):
        self.folder.invokeFactory("Document", id="item1")
        self.folder.invokeFactory("Folder", id="folder1")
        self.folder.invokeFactory("Document", id="foo")
        r = check_id(self.folder.folder1.foo, "item1")
        self.assertEqual(r, None)

    def testInvalidId(self):
        self.folder._setObject("foo", dummy.Item("foo"))
        r = check_id(self.folder.foo, "_foo")
        self.assertEqual(r, "_foo is reserved.")

    def testContainerHook(self):
        # Container may have a checkValidId method; make sure it is called
        self.folder._setObject("checkValidId", dummy.Raiser(dummy.Error))
        self.folder._setObject("foo", dummy.Item("foo"))
        r = check_id(self.folder.foo, "whatever")
        self.assertEqual(r, "whatever is reserved.")

    def testContainerHookRaisesUnauthorized(self):
        # check_id does not raise Unauthorized errors raised by hook
        self.folder._setObject("checkValidId", dummy.Raiser(Unauthorized))
        self.folder._setObject("foo", dummy.Item("foo"))
        r = check_id(self.folder.foo, "whatever")
        self.assertEqual(r, "whatever is reserved.")

    def testContainerHookRaisesConflictError(self):
        # check_id should not swallow ConflictErrors raised by hook
        self.folder._setObject("checkValidId", dummy.Raiser(ConflictError))
        self.folder._setObject("foo", dummy.Item("foo"))
        with self.assertRaises(ConflictError):
            check_id(self.folder.foo, "whatever")

    def testMissingUtils(self):
        # check_id should not bomb out if the plone_utils tool is missing
        self.portal._delObject("plone_utils")
        r = check_id(self.folder, "foo")
        self.assertEqual(r, None)  # success

    def testMissingCatalog(self):
        # check_id should not bomb out if the portal_catalog tool is missing
        self.portal._delObject("portal_catalog")
        r = check_id(self.folder, "foo")
        self.assertEqual(r, None)  # success

    def testMissingFactory(self):
        # check_id should not bomb out if the portal_factory tool is missing
        if "portal_factory" in self.portal:
            self.portal._delObject("portal_factory")
        r = check_id(self.folder, "foo")
        self.assertEqual(r, None)  # success

    def testCatalogIndexSkipped(self):
        # Note that the check is skipped when we don't have
        # the "Search ZCatalogs" permission.
        self.portal.manage_permission("Search ZCatalog", ["Manager"], acquire=0)

        r = check_id(self.folder, "created")
        # But now the final hasattr check picks this up
        self.assertEqual(r, "created is reserved.")

    def testCollisionNotSkipped(self):
        # Note that the existing object check is done, even when we don't have
        # the "Access contents information" permission.
        # This used to be the other way around.  The reason got lost.
        # Probably this was because the permission was checked automatically
        # because check_id was a skin script.  Since Plone 5.2 it is a
        # function which cannot be accessed from the web or templates,
        # so the permission test seems unneeded.
        self.folder.manage_permission("Access contents information", [], acquire=0)

        self.folder._setObject("foo", dummy.Item("foo"))
        self.folder._setObject("bar", dummy.Item("bar"))
        r = check_id(self.folder.foo, "bar")
        self.assertEqual(r, "bar is reserved.")

    def testReservedIdSkipped(self):
        # This check is picked up by the checkIdAvailable, unless we don't have
        # the "Add portal content" permission, in which case it is picked up by
        # the final hasattr check.
        self.folder.manage_permission("Add portal content", [], acquire=0)

        self.folder._setObject("foo", dummy.Item("foo"))
        r = check_id(self.folder.foo, "portal_catalog")
        self.assertEqual(r, "portal_catalog is reserved.")

    def testInvalidIdSkipped(self):
        # Note that the check is skipped when we don't have
        # the "Add portal content" permission.
        self.folder.manage_permission("Add portal content", [], acquire=0)

        self.folder._setObject("foo", dummy.Item("foo"))
        r = check_id(self.folder.foo, "_foo")
        self.assertEqual(r, None)  # success

    def testParentMethodAliasDisallowed(self):
        # Note that the check is skipped when we don't have
        # the "Add portal content" permission.
        self.folder.manage_permission("Add portal content", ["Manager"], acquire=0)

        self.folder._setObject("foo", dummy.Item("foo"))
        for alias in self.folder.getTypeInfo().getMethodAliases().keys():
            r = check_id(self.folder.foo, alias)
            self.assertEqual(r, "%s is reserved." % alias)

    def testCheckingMethodAliasesOnPortalRoot(self):
        # Test for bug http://dev.plone.org/plone/ticket/4351
        self.setRoles(["Manager"])
        self.portal.manage_permission("Add portal content", ["Manager"], acquire=0)

        # Should not raise: Before we were using obj.getTypeInfo(), which is
        # not defined on the portal root.
        try:
            check_id(self.portal, "foo")
        except AttributeError as e:
            self.fail(e)
