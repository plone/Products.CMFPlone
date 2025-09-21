from datetime import datetime
from datetime import timedelta
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.base.interfaces.recyclebin import IRecycleBin
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.controlpanel.browser.recyclebin import (
    IRecycleBinControlPanelSettings,
)
from Products.CMFPlone.recyclebin import ANNOTATION_KEY
from unittest import mock
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility

import unittest


class RecycleBinTestCase(unittest.TestCase):
    """Base test case for RecycleBin tests"""

    layer = IntegrationTesting(
        bases=(PLONE_FIXTURE,), name="RecycleBinTests:Integration"
    )

    def setUp(self):
        """Set up the test environment"""
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        # Log in as a manager
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)

        # Get the registry to access recycle bin settings
        self.registry = getUtility(IRegistry)

        # Enable the recycle bin
        self.registry.forInterface(
            IRecycleBinControlPanelSettings, prefix="plone-recyclebin"
        ).recycling_enabled = True

        # Set a short retention period for testing
        self.registry.forInterface(
            IRecycleBinControlPanelSettings, prefix="plone-recyclebin"
        ).retention_period = 30

        # Set a reasonable maximum size
        self.registry.forInterface(
            IRecycleBinControlPanelSettings, prefix="plone-recyclebin"
        ).maximum_size = 100  # 100 MB

        # Get the recycle bin utility
        self.recyclebin = getUtility(IRecycleBin)

        # Clear any existing items from the recycle bin
        annotations = IAnnotations(self.portal)
        if ANNOTATION_KEY in annotations:
            del annotations[ANNOTATION_KEY]

    def tearDown(self):
        """Clean up after the test"""
        # Clear the recycle bin
        annotations = IAnnotations(self.portal)
        if ANNOTATION_KEY in annotations:
            del annotations[ANNOTATION_KEY]


class RecycleBinSetupTests(RecycleBinTestCase):
    """Tests for RecycleBin setup and configuration"""

    def test_recyclebin_enabled(self):
        """Test that the recycle bin is initialized and enabled"""
        self.assertTrue(self.recyclebin.is_enabled())

    def test_recyclebin_storage(self):
        """Test that the storage is correctly initialized"""
        storage = self.recyclebin.storage
        self.assertEqual(len(storage), 0)
        self.assertEqual(list(storage.keys()), [])

    def test_recyclebin_settings(self):
        """Test that the settings are correctly initialized"""
        settings = self.recyclebin._get_settings()
        self.assertTrue(settings.recycling_enabled)
        self.assertEqual(settings.retention_period, 30)
        self.assertEqual(settings.maximum_size, 100)

    def test_recyclebin_permission(self):
        """Test permission checks for the recycle bin"""
        # As Manager role, should have access
        self.assertTrue(self.recyclebin.check_permission())

        self.portal.acl_users._doAddUser("testuser", "password", ["Member"], [])

        # Log in as the test user using plone.app.testing login function
        login(self.portal, "testuser")

        # Check permission - should be False for a regular member
        self.assertFalse(self.recyclebin.check_permission())


class RecycleBinContentTests(RecycleBinTestCase):
    """Tests for deleting and restoring basic content items"""

    def setUp(self):
        """Set up test content"""
        super().setUp()

        # Create a page
        self.portal.invokeFactory("Document", "test-page", title="Test Page")
        self.page = self.portal["test-page"]

        # Create a news item
        self.portal.invokeFactory("News Item", "test-news", title="Test News")
        self.news = self.portal["test-news"]

    def test_delete_restore_page(self):
        """Test deleting and restoring a page"""
        # Get the original path
        page_path = "/".join(self.page.getPhysicalPath())
        page_id = self.page.getId()
        page_title = self.page.Title()

        # Delete the page by adding it to the recycle bin
        recycle_id = self.recyclebin.add_item(self.page, self.portal, page_path)

        # Verify it was added to the recycle bin
        self.assertIsNotNone(recycle_id)
        self.assertIn(recycle_id, self.recyclebin.storage)

        # Verify the page metadata was stored correctly
        item_data = self.recyclebin.storage[recycle_id]
        self.assertEqual(item_data["id"], page_id)
        self.assertEqual(item_data["title"], page_title)
        self.assertEqual(item_data["type"], "Document")
        self.assertEqual(item_data["path"], page_path)
        self.assertIsInstance(item_data["deletion_date"], datetime)

        # Verify the page is in the recycle bin listing
        items = self.recyclebin.get_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], page_id)
        self.assertEqual(items[0]["recycle_id"], recycle_id)

        # Verify we can get the item directly
        item = self.recyclebin.get_item(recycle_id)
        self.assertEqual(item["id"], page_id)

        # Remove the original page from the portal to simulate deletion
        del self.portal[page_id]
        self.assertNotIn(page_id, self.portal)

        # Restore the page
        restored_page = self.recyclebin.restore_item(recycle_id)

        # Verify the page was restored
        self.assertIsNotNone(restored_page)
        self.assertEqual(restored_page.getId(), page_id)
        self.assertEqual(restored_page.Title(), page_title)

        # Verify the page is back in the portal
        self.assertIn(page_id, self.portal)

        # Verify the item was removed from the recycle bin
        self.assertNotIn(recycle_id, self.recyclebin.storage)
        items = self.recyclebin.get_items()

    def test_delete_restore_news(self):
        """Test deleting and restoring a news item"""
        # Get the original path
        news_path = "/".join(self.news.getPhysicalPath())
        news_id = self.news.getId()
        news_title = self.news.Title()

        # Delete the news item by adding it to the recycle bin
        recycle_id = self.recyclebin.add_item(self.news, self.portal, news_path)

        # Verify it was added to the recycle bin
        self.assertIsNotNone(recycle_id)
        self.assertIn(recycle_id, self.recyclebin.storage)

        # Verify the news metadata was stored correctly
        item_data = self.recyclebin.storage[recycle_id]
        self.assertEqual(item_data["id"], news_id)
        self.assertEqual(item_data["title"], news_title)
        self.assertEqual(item_data["type"], "News Item")
        self.assertEqual(item_data["path"], news_path)
        self.assertIsInstance(item_data["deletion_date"], datetime)

        # Remove the original news item from the portal to simulate deletion
        del self.portal[news_id]
        self.assertNotIn(news_id, self.portal)

        # Restore the news item
        restored_news = self.recyclebin.restore_item(recycle_id)

        # Verify the news item was restored
        self.assertIsNotNone(restored_news)
        self.assertEqual(restored_news.getId(), news_id)
        self.assertEqual(restored_news.Title(), news_title)

        # Verify the news item is back in the portal
        self.assertIn(news_id, self.portal)

        # Verify the item was removed from the recycle bin
        self.assertNotIn(recycle_id, self.recyclebin.storage)

    def test_purge_item(self):
        """Test purging an item from the recycle bin"""
        # Delete the page
        page_path = "/".join(self.page.getPhysicalPath())
        recycle_id = self.recyclebin.add_item(self.page, self.portal, page_path)

        # Verify it was added to the recycle bin
        self.assertIn(recycle_id, self.recyclebin.storage)

        # Purge the item
        result = self.recyclebin.purge_item(recycle_id)

        # Verify the item was purged
        self.assertTrue(result)
        self.assertNotIn(recycle_id, self.recyclebin.storage)

        # Verify the item is not in the listing
        items = self.recyclebin.get_items()
        self.assertEqual(len(items), 0)


class RecycleBinFolderTests(RecycleBinTestCase):
    """Tests for deleting and restoring folder structures"""

    def setUp(self):
        """Set up test content"""
        super().setUp()

        # Create a folder
        self.portal.invokeFactory("Folder", "test-folder", title="Test Folder")
        self.folder = self.portal["test-folder"]

        # Add content to the folder
        self.folder.invokeFactory("Document", "folder-page", title="Folder Page")
        self.folder.invokeFactory("News Item", "folder-news", title="Folder News")

    def test_delete_restore_folder(self):
        """Test deleting and restoring a folder with content"""
        # Get the original path
        folder_path = "/".join(self.folder.getPhysicalPath())
        folder_id = self.folder.getId()
        folder_title = self.folder.Title()

        # Delete the folder by adding it to the recycle bin
        recycle_id = self.recyclebin.add_item(self.folder, self.portal, folder_path)

        # Verify it was added to the recycle bin
        self.assertIsNotNone(recycle_id)
        self.assertIn(recycle_id, self.recyclebin.storage)

        # Verify the folder metadata was stored correctly
        item_data = self.recyclebin.storage[recycle_id]
        self.assertEqual(item_data["id"], folder_id)
        self.assertEqual(item_data["title"], folder_title)
        self.assertEqual(item_data["type"], "Folder")
        self.assertEqual(item_data["path"], folder_path)
        self.assertIsInstance(item_data["deletion_date"], datetime)

        # Verify the children were tracked
        self.assertIn("children", item_data)
        self.assertEqual(item_data["children_count"], 2)
        self.assertIn("folder-page", item_data["children"])
        self.assertIn("folder-news", item_data["children"])

        # Remove the original folder from the portal to simulate deletion
        del self.portal[folder_id]
        self.assertNotIn(folder_id, self.portal)

        # Restore the folder
        restored_folder = self.recyclebin.restore_item(recycle_id)

        # Verify the folder was restored
        self.assertIsNotNone(restored_folder)
        self.assertEqual(restored_folder.getId(), folder_id)
        self.assertEqual(restored_folder.Title(), folder_title)

        # Verify the folder is back in the portal
        self.assertIn(folder_id, self.portal)

        # Verify the contents were restored
        self.assertIn("folder-page", restored_folder)
        self.assertIn("folder-news", restored_folder)
        self.assertEqual(restored_folder["folder-page"].Title(), "Folder Page")
        self.assertEqual(restored_folder["folder-news"].Title(), "Folder News")

        # Verify the item was removed from the recycle bin
        self.assertNotIn(recycle_id, self.recyclebin.storage)

    def test_purge_folder_with_contents(self):
        """Test purging a folder with content completely removes all related items"""
        # Get the original path
        folder_path = "/".join(self.folder.getPhysicalPath())
        page_path = "/".join(self.folder["folder-page"].getPhysicalPath())
        news_path = "/".join(self.folder["folder-news"].getPhysicalPath())

        # Delete the folder and its contents by adding them individually to the recycle bin
        # This simulates how the recycle bin typically receives items when a folder is deleted
        folder_recycle_id = self.recyclebin.add_item(
            self.folder, self.portal, folder_path
        )
        page_recycle_id = self.recyclebin.add_item(
            self.folder["folder-page"], self.folder, page_path
        )
        news_recycle_id = self.recyclebin.add_item(
            self.folder["folder-news"], self.folder, news_path
        )

        # Verify all items were added to the recycle bin
        self.assertIn(folder_recycle_id, self.recyclebin.storage)
        self.assertIn(page_recycle_id, self.recyclebin.storage)
        self.assertIn(news_recycle_id, self.recyclebin.storage)

        # Get all items before purging
        before_items = self.recyclebin.get_items()
        self.assertEqual(len(before_items), 3)

        # Purge just the folder item
        result = self.recyclebin.purge_item(folder_recycle_id)
        self.assertTrue(result)

        # Verify all related items were purged
        self.assertNotIn(folder_recycle_id, self.recyclebin.storage)
        self.assertNotIn(page_recycle_id, self.recyclebin.storage)
        self.assertNotIn(news_recycle_id, self.recyclebin.storage)

        # Verify no items remain in the listing
        after_items = self.recyclebin.get_items()
        self.assertEqual(len(after_items), 0)


class RecycleBinNestedFolderTests(RecycleBinTestCase):
    """Tests for deleting and restoring nested folder structures"""

    def setUp(self):
        """Set up test content"""
        super().setUp()

        # Create a parent folder
        self.portal.invokeFactory("Folder", "parent-folder", title="Parent Folder")
        self.parent_folder = self.portal["parent-folder"]

        # Create a nested folder
        self.parent_folder.invokeFactory("Folder", "child-folder", title="Child Folder")
        self.child_folder = self.parent_folder["child-folder"]

        # Add content to the nested folder
        self.child_folder.invokeFactory("Document", "nested-page", title="Nested Page")
        self.child_folder.invokeFactory("News Item", "nested-news", title="Nested News")

        # Create another level of nesting
        self.child_folder.invokeFactory(
            "Folder", "grandchild-folder", title="Grandchild Folder"
        )
        self.grandchild_folder = self.child_folder["grandchild-folder"]

        # Add content to the grandchild folder
        self.grandchild_folder.invokeFactory("Document", "deep-page", title="Deep Page")

    def test_delete_restore_nested_folder(self):
        """Test deleting and restoring a nested folder structure"""
        # Get the original paths
        parent_path = "/".join(self.parent_folder.getPhysicalPath())
        parent_id = self.parent_folder.getId()

        # Delete the parent folder by adding it to the recycle bin
        recycle_id = self.recyclebin.add_item(
            self.parent_folder, self.portal, parent_path
        )

        # Verify it was added to the recycle bin
        self.assertIsNotNone(recycle_id)
        self.assertIn(recycle_id, self.recyclebin.storage)

        # Verify the parent folder metadata was stored correctly
        item_data = self.recyclebin.storage[recycle_id]
        self.assertEqual(item_data["id"], parent_id)
        self.assertEqual(item_data["type"], "Folder")

        # Verify the children were tracked
        self.assertIn("children", item_data)
        self.assertEqual(item_data["children_count"], 1)
        self.assertIn("child-folder", item_data["children"])

        # Verify the nested children were tracked
        child_data = item_data["children"]["child-folder"]
        self.assertIn("children", child_data)
        self.assertEqual(child_data["children_count"], 3)
        self.assertIn("nested-page", child_data["children"])
        self.assertIn("nested-news", child_data["children"])
        self.assertIn("grandchild-folder", child_data["children"])

        # Verify the deepest level was tracked
        grandchild_data = child_data["children"]["grandchild-folder"]
        self.assertIn("children", grandchild_data)
        self.assertEqual(grandchild_data["children_count"], 1)
        self.assertIn("deep-page", grandchild_data["children"])

        # Remove the parent folder from the portal to simulate deletion
        del self.portal[parent_id]
        self.assertNotIn(parent_id, self.portal)

        # Restore the parent folder
        restored_folder = self.recyclebin.restore_item(recycle_id)

        # Verify the parent folder was restored
        self.assertIsNotNone(restored_folder)
        self.assertEqual(restored_folder.getId(), parent_id)
        self.assertIn(parent_id, self.portal)

        # Verify the child folder was restored
        self.assertIn("child-folder", restored_folder)
        restored_child = restored_folder["child-folder"]

        # Verify the nested content was restored
        self.assertIn("nested-page", restored_child)
        self.assertIn("nested-news", restored_child)
        self.assertIn("grandchild-folder", restored_child)

        # Verify the deepest level was restored
        restored_grandchild = restored_child["grandchild-folder"]
        self.assertIn("deep-page", restored_grandchild)

        # Verify the item was removed from the recycle bin
        self.assertNotIn(recycle_id, self.recyclebin.storage)

    def test_delete_restore_middle_folder(self):
        """Test deleting and restoring a middle-level folder"""
        # Get the original paths
        child_path = "/".join(self.child_folder.getPhysicalPath())
        child_id = self.child_folder.getId()

        # Delete the child folder by adding it to the recycle bin
        recycle_id = self.recyclebin.add_item(
            self.child_folder, self.parent_folder, child_path
        )

        # Verify it was added to the recycle bin
        self.assertIsNotNone(recycle_id)
        self.assertIn(recycle_id, self.recyclebin.storage)

        # Verify the child folder metadata was stored correctly
        item_data = self.recyclebin.storage[recycle_id]
        self.assertEqual(item_data["id"], child_id)
        self.assertEqual(item_data["type"], "Folder")

        # Verify the nested children were tracked
        self.assertIn("children", item_data)
        self.assertEqual(item_data["children_count"], 3)

        # Remove the child folder from the parent folder to simulate deletion
        del self.parent_folder[child_id]
        self.assertNotIn(child_id, self.parent_folder)

        # Restore the child folder
        restored_folder = self.recyclebin.restore_item(recycle_id)

        # Verify the child folder was restored
        self.assertIsNotNone(restored_folder)
        self.assertEqual(restored_folder.getId(), child_id)
        self.assertIn(child_id, self.parent_folder)

        # Verify the nested content was restored
        self.assertIn("nested-page", restored_folder)
        self.assertIn("nested-news", restored_folder)
        self.assertIn("grandchild-folder", restored_folder)

        # Verify the deepest level was restored
        restored_grandchild = restored_folder["grandchild-folder"]
        self.assertIn("deep-page", restored_grandchild)

        # Verify the item was removed from the recycle bin
        self.assertNotIn(recycle_id, self.recyclebin.storage)


class RecycleBinExpirationTests(RecycleBinTestCase):
    """Tests for recyclebin expiration and size limit functionality"""

    def test_purge_expired_items(self):
        """Test purging expired items based on retention period"""
        # Create a page
        self.portal.invokeFactory("Document", "expired-page", title="Expired Page")
        page = self.portal["expired-page"]
        page_path = "/".join(page.getPhysicalPath())

        # Add it to the recycle bin
        recycle_id = self.recyclebin.add_item(page, self.portal, page_path)

        # Verify it was added
        self.assertIn(recycle_id, self.recyclebin.storage)

        # Mock the deletion date to be older than the retention period
        with mock.patch.dict(
            self.recyclebin.storage[recycle_id],
            {"deletion_date": datetime.now() - timedelta(days=31)},
        ):
            # Call _purge_expired_items
            purged_count = self.recyclebin._purge_expired_items()

            # Verify the item was purged
            self.assertEqual(purged_count, 1)
            self.assertNotIn(recycle_id, self.recyclebin.storage)


class RecycleBinRestoreEdgeCaseTests(RecycleBinTestCase):
    """Tests for edge cases when restoring items"""

    def test_restore_with_parent_gone(self):
        """Test restoring an item when its parent container is gone"""
        # Create a folder and a document inside it
        self.portal.invokeFactory("Folder", "temp-folder", title="Temporary Folder")
        folder = self.portal["temp-folder"]
        folder.invokeFactory("Document", "orphan-page", title="Orphan Page")
        page = folder["orphan-page"]
        page_path = "/".join(page.getPhysicalPath())

        # Add the page to the recycle bin
        recycle_id = self.recyclebin.add_item(page, folder, page_path)

        # Delete the folder to simulate parent container being gone
        del self.portal["temp-folder"]

        # Trying to restore without a target container should return an error dictionary
        result = self.recyclebin.restore_item(recycle_id)
        self.assertIsInstance(result, dict)
        self.assertFalse(
            result.get("success", True)
        )  # Should be marked as unsuccessful
        self.assertIn("error", result)  # Should contain an error message

        # Now restore with an explicit target container
        restored_page = self.recyclebin.restore_item(
            recycle_id, target_container=self.portal
        )

        # Verify the page was restored to the portal
        self.assertIsNotNone(restored_page)
        self.assertEqual(restored_page.getId(), "orphan-page")
        self.assertIn("orphan-page", self.portal)

    def test_restore_with_name_conflict(self):
        """Test restoring an item when an item with same id already exists"""
        # Create a page
        self.portal.invokeFactory("Document", "conflict-page2", title="Original Page")
        page = self.portal["conflict-page2"]
        page_path = "/".join(page.getPhysicalPath())
        page_id = page.getId()

        # Add it to the recycle bin
        recycle_id = self.recyclebin.add_item(page, self.portal, page_path)

        # Remove the original page from the portal to simulate deletion
        del self.portal[page_id]
        self.assertNotIn(page_id, self.portal)

        # Create another page with the same ID
        self.portal.invokeFactory(
            "Document", "conflict-page2", title="Replacement Page"
        )

        # Since the ID already exists, it should raise an error
        with self.assertRaises(ValueError):
            # Restore the item
            self.recyclebin.restore_item(recycle_id)

    def test_restore_with_parent_gone_to_target(self):
        """Test restoring an item when its parent container is gone, should restore to target container"""
        # Create a folder and a document inside it
        self.portal.invokeFactory("Folder", "parent-folder", title="Parent Folder")
        folder = self.portal["parent-folder"]
        folder.invokeFactory("Document", "child-page", title="Child Page")
        page = folder["child-page"]
        page_path = "/".join(page.getPhysicalPath())

        # Add the page to the recycle bin
        recycle_id = self.recyclebin.add_item(page, folder, page_path)

        # Delete the folder to simulate parent container being gone
        del self.portal["parent-folder"]

        # Create a new target folder
        self.portal.invokeFactory("Folder", "target-folder", title="Target Folder")
        target_folder = self.portal["target-folder"]

        # Now restore with the target folder as container
        restored_page = self.recyclebin.restore_item(
            recycle_id, target_container=target_folder
        )

        # Verify the page was restored to the target folder
        self.assertIsNotNone(restored_page)
        self.assertEqual(restored_page.getId(), "child-page")
        self.assertIn("child-page", target_folder)
        self.assertEqual(target_folder["child-page"].Title(), "Child Page")

        # Verify the item was removed from the recycle bin
        self.assertNotIn(recycle_id, self.recyclebin.storage)
