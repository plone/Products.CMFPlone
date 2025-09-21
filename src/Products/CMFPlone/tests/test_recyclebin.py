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
        self.assertFalse(settings.restore_to_initial_state)


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
        self.assertIn("deleted_by", item_data)
        self.assertIsInstance(item_data["deleted_by"], str)

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

    def test_deleted_by_field(self):
        """Test that deleted_by field is properly stored and retrieved"""
        # Delete the page
        page_path = "/".join(self.page.getPhysicalPath())
        recycle_id = self.recyclebin.add_item(self.page, self.portal, page_path)

        # Verify it was added to the recycle bin
        self.assertIn(recycle_id, self.recyclebin.storage)

        # Check that deleted_by is stored in the raw storage
        item_data = self.recyclebin.storage[recycle_id]
        self.assertIn("deleted_by", item_data)
        self.assertIsInstance(item_data["deleted_by"], str)
        self.assertEqual(item_data["deleted_by"], TEST_USER_ID)

        # Check that deleted_by is included in get_items() result
        items = self.recyclebin.get_items()
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertIn("deleted_by", item)
        self.assertEqual(item["deleted_by"], TEST_USER_ID)

        # Check that deleted_by is included in get_item() result
        retrieved_item = self.recyclebin.get_item(recycle_id)
        self.assertIsNotNone(retrieved_item)
        self.assertIn("deleted_by", retrieved_item)
        self.assertEqual(retrieved_item["deleted_by"], TEST_USER_ID)


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


class RecycleBinWorkflowTests(RecycleBinTestCase):
    """Tests for workflow state restoration functionality"""

    def setUp(self):
        """Set up test content with workflow states"""
        super().setUp()
        
        # Create a document and publish it
        self.portal.invokeFactory("Document", "published-page", title="Published Page")
        self.page = self.portal["published-page"]
        
        # Get workflow tool
        from Products.CMFCore.utils import getToolByName
        self.workflow_tool = getToolByName(self.portal, "portal_workflow")
        
        # Publish the page (move from initial state to published)
        self.workflow_tool.doActionFor(self.page, "publish")
        
        # Verify the page is published
        self.assertEqual(
            self.workflow_tool.getInfoFor(self.page, "review_state"), "published"
        )

    def test_restore_without_workflow_reset(self):
        """Test that restoration preserves original workflow state by default"""
        # Add the published page to recycle bin
        page_path = "/".join(self.page.getPhysicalPath())
        recycle_id = self.recyclebin.add_item(self.page, self.portal, page_path)
        
        # Remove the page from portal
        del self.portal[self.page.getId()]
        
        # Verify restore_to_initial_state is False by default
        settings = self.recyclebin._get_settings()
        self.assertFalse(settings.restore_to_initial_state)
        
        # Restore the item
        restored_page = self.recyclebin.restore_item(recycle_id)
        
        # Verify the page is still in published state
        self.assertIsNotNone(restored_page)
        self.assertEqual(
            self.workflow_tool.getInfoFor(restored_page, "review_state"), "published"
        )

    def test_restore_with_workflow_reset(self):
        """Test that restoration resets to initial state when setting is enabled"""
        # Enable workflow state reset
        settings = self.registry.forInterface(
            IRecycleBinControlPanelSettings, prefix="plone-recyclebin"
        )
        settings.restore_to_initial_state = True
        
        # Add the published page to recycle bin
        page_path = "/".join(self.page.getPhysicalPath())
        recycle_id = self.recyclebin.add_item(self.page, self.portal, page_path)
        
        # Remove the page from portal
        del self.portal[self.page.getId()]
        
        # Restore the item
        restored_page = self.recyclebin.restore_item(recycle_id)
        
        # Verify the page was reset to initial state (usually 'private' in Plone)
        self.assertIsNotNone(restored_page)
        restored_state = self.workflow_tool.getInfoFor(restored_page, "review_state")
        
        # Get the initial state of the workflow for this type
        workflow_chain = self.workflow_tool.getChainFor(restored_page)
        if workflow_chain:
            workflow = self.workflow_tool.getWorkflowById(workflow_chain[0])
            initial_state = workflow.initial_state
            self.assertEqual(restored_state, initial_state)

    def test_restore_folder_with_workflow_reset(self):
        """Test that folder children also get their workflow states reset"""
        # Create a folder with children
        self.portal.invokeFactory("Folder", "test-folder", title="Test Folder")
        folder = self.portal["test-folder"]
        
        # Create and publish a child document
        folder.invokeFactory("Document", "child-page", title="Child Page")
        child_page = folder["child-page"]
        self.workflow_tool.doActionFor(child_page, "publish")
        
        # Verify child is published
        self.assertEqual(
            self.workflow_tool.getInfoFor(child_page, "review_state"), "published"
        )
        
        # Enable workflow state reset
        settings = self.registry.forInterface(
            IRecycleBinControlPanelSettings, prefix="plone-recyclebin"
        )
        settings.restore_to_initial_state = True
        
        # Add the folder to recycle bin
        folder_path = "/".join(folder.getPhysicalPath())
        recycle_id = self.recyclebin.add_item(folder, self.portal, folder_path)
        
        # Remove the folder from portal
        del self.portal[folder.getId()]
        
        # Restore the folder
        restored_folder = self.recyclebin.restore_item(recycle_id)
        
        # Verify the folder was restored
        self.assertIsNotNone(restored_folder)
        self.assertIn("child-page", restored_folder)
        
        # Verify the child's workflow state was reset to initial state
        restored_child = restored_folder["child-page"]
        child_state = self.workflow_tool.getInfoFor(restored_child, "review_state")
        
        # Get the initial state of the workflow for this type
        workflow_chain = self.workflow_tool.getChainFor(restored_child)
        if workflow_chain:
            workflow = self.workflow_tool.getWorkflowById(workflow_chain[0])
            initial_state = workflow.initial_state
            self.assertEqual(child_state, initial_state)


class RecycleBinViewTests(RecycleBinTestCase):
    """Tests for RecycleBinView date filtering functionality"""

    def setUp(self):
        """Set up test content with different deletion dates"""
        super().setUp()
        
        # Create test documents with different deletion dates
        self.portal.invokeFactory("Document", "doc1", title="Document 1")
        self.portal.invokeFactory("Document", "doc2", title="Document 2")
        self.portal.invokeFactory("Document", "doc3", title="Document 3")
        
        self.doc1 = self.portal["doc1"]
        self.doc2 = self.portal["doc2"]
        self.doc3 = self.portal["doc3"]

        # Create a mock request for the view
        from unittest.mock import Mock
        self.request = Mock()
        self.request.form = {}
        
        # Create the view instance
        from Products.CMFPlone.browser.recyclebin import RecycleBinView
        self.view = RecycleBinView(self.portal, self.request)

    def test_get_date_from(self):
        """Test get_date_from method"""
        # Test with no date_from parameter
        self.assertEqual(self.view.get_date_from(), "")
        
        # Test with date_from parameter
        self.request.form["date_from"] = "2024-01-01"
        self.assertEqual(self.view.get_date_from(), "2024-01-01")

    def test_get_date_to(self):
        """Test get_date_to method"""
        # Test with no date_to parameter
        self.assertEqual(self.view.get_date_to(), "")
        
        # Test with date_to parameter
        self.request.form["date_to"] = "2024-12-31"
        self.assertEqual(self.view.get_date_to(), "2024-12-31")

    def test_get_filter_deleted_by(self):
        """Test get_filter_deleted_by method"""
        # Test with no filter_deleted_by parameter
        self.assertEqual(self.view.get_filter_deleted_by(), "")
        
        # Test with filter_deleted_by parameter
        self.request.form["filter_deleted_by"] = "admin"
        self.assertEqual(self.view.get_filter_deleted_by(), "admin")

    def test_get_available_deleted_by_users(self):
        """Test get_available_deleted_by_users method"""
        items = [
            {"deleted_by": "admin"},
            {"deleted_by": "user1"},
            {"deleted_by": "admin"},  # duplicate
            {"deleted_by": "user2"},
            {"title": "item without deleted_by"},  # no deleted_by field
        ]
        
        users = self.view.get_available_deleted_by_users(items)
        expected_users = ["admin", "user1", "user2"]
        self.assertEqual(users, expected_users)

    def test_get_available_deleted_by_users_empty(self):
        """Test get_available_deleted_by_users with empty list"""
        items = []
        users = self.view.get_available_deleted_by_users(items)
        self.assertEqual(users, [])

    def test_check_item_matches_date_range_no_filter(self):
        """Test date range filtering with no date filters"""
        item = {"deletion_date": datetime.now()}
        
        # No date filters should match all items
        self.assertTrue(self.view._check_item_matches_date_range(item, "", ""))

    def test_check_item_matches_date_range_with_from_date(self):
        """Test date range filtering with from date only"""
        # Create items with different dates
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        item_today = {"deletion_date": today}
        item_yesterday = {"deletion_date": yesterday}
        item_tomorrow = {"deletion_date": tomorrow}
        
        from_date = today.strftime("%Y-%m-%d")
        
        # Item from today should match (same date)
        self.assertTrue(self.view._check_item_matches_date_range(item_today, from_date, ""))
        
        # Item from yesterday should not match (before from_date)
        self.assertFalse(self.view._check_item_matches_date_range(item_yesterday, from_date, ""))
        
        # Item from tomorrow should match (after from_date)
        self.assertTrue(self.view._check_item_matches_date_range(item_tomorrow, from_date, ""))

    def test_check_item_matches_date_range_with_to_date(self):
        """Test date range filtering with to date only"""
        # Create items with different dates
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        item_today = {"deletion_date": today}
        item_yesterday = {"deletion_date": yesterday}
        item_tomorrow = {"deletion_date": tomorrow}
        
        to_date = today.strftime("%Y-%m-%d")
        
        # Item from today should match (same date)
        self.assertTrue(self.view._check_item_matches_date_range(item_today, "", to_date))
        
        # Item from yesterday should match (before to_date)
        self.assertTrue(self.view._check_item_matches_date_range(item_yesterday, "", to_date))
        
        # Item from tomorrow should not match (after to_date)
        self.assertFalse(self.view._check_item_matches_date_range(item_tomorrow, "", to_date))

    def test_check_item_matches_date_range_with_both_dates(self):
        """Test date range filtering with both from and to dates"""
        # Create items with different dates
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        day_before_yesterday = today - timedelta(days=2)
        day_after_tomorrow = today + timedelta(days=2)
        
        item_today = {"deletion_date": today}
        item_yesterday = {"deletion_date": yesterday}
        item_tomorrow = {"deletion_date": tomorrow}
        item_before = {"deletion_date": day_before_yesterday}
        item_after = {"deletion_date": day_after_tomorrow}
        
        from_date = yesterday.strftime("%Y-%m-%d")
        to_date = tomorrow.strftime("%Y-%m-%d")
        
        # Items within range should match
        self.assertTrue(self.view._check_item_matches_date_range(item_yesterday, from_date, to_date))
        self.assertTrue(self.view._check_item_matches_date_range(item_today, from_date, to_date))
        self.assertTrue(self.view._check_item_matches_date_range(item_tomorrow, from_date, to_date))
        
        # Items outside range should not match
        self.assertFalse(self.view._check_item_matches_date_range(item_before, from_date, to_date))
        self.assertFalse(self.view._check_item_matches_date_range(item_after, from_date, to_date))

    def test_check_item_matches_date_range_invalid_date_format(self):
        """Test date range filtering with invalid date formats"""
        item = {"deletion_date": datetime.now()}
        
        # Invalid date formats should be ignored (return True)
        self.assertTrue(self.view._check_item_matches_date_range(item, "invalid-date", ""))
        self.assertTrue(self.view._check_item_matches_date_range(item, "", "invalid-date"))
        self.assertTrue(self.view._check_item_matches_date_range(item, "invalid", "also-invalid"))

    def test_check_item_matches_date_range_no_deletion_date(self):
        """Test date range filtering with items that have no deletion_date"""
        item = {"title": "Item without deletion date"}
        
        # Items without deletion_date should not match any date filter
        self.assertFalse(self.view._check_item_matches_date_range(item, "2024-01-01", ""))
        self.assertFalse(self.view._check_item_matches_date_range(item, "", "2024-12-31"))
        self.assertFalse(self.view._check_item_matches_date_range(item, "2024-01-01", "2024-12-31"))

    def test_get_clear_url_with_date_filters(self):
        """Test clear URL generation with date and deleted_by filters"""
        # Set up request with multiple filters including dates and deleted_by
        self.request.form = {
            "search_query": "test",
            "filter_type": "Document",
            "date_from": "2024-01-01",
            "date_to": "2024-12-31",
            "filter_deleted_by": "admin",
            "sort_by": "title_asc"
        }
        
        # Test clearing date_from while preserving others
        clear_url = self.view.get_clear_url("date_from")
        self.assertIn("search_query=test", clear_url)
        self.assertIn("filter_type=Document", clear_url)
        self.assertIn("date_to=2024-12-31", clear_url)
        self.assertIn("filter_deleted_by=admin", clear_url)
        self.assertIn("sort_by=title_asc", clear_url)
        self.assertNotIn("date_from", clear_url)
        
        # Test clearing date_to while preserving others
        clear_url = self.view.get_clear_url("date_to")
        self.assertIn("search_query=test", clear_url)
        self.assertIn("filter_type=Document", clear_url)
        self.assertIn("date_from=2024-01-01", clear_url)
        self.assertIn("filter_deleted_by=admin", clear_url)
        self.assertIn("sort_by=title_asc", clear_url)
        self.assertNotIn("date_to", clear_url)
        
        # Test clearing filter_deleted_by while preserving others
        clear_url = self.view.get_clear_url("filter_deleted_by")
        self.assertIn("search_query=test", clear_url)
        self.assertIn("filter_type=Document", clear_url)
        self.assertIn("date_from=2024-01-01", clear_url)
        self.assertIn("date_to=2024-12-31", clear_url)
        self.assertIn("sort_by=title_asc", clear_url)
        self.assertNotIn("filter_deleted_by", clear_url)
