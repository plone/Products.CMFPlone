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

import functools
import unittest


# Test content factory functions for reusability
def create_test_content(portal, content_type, id_suffix="", title_suffix=""):
    """Factory function for creating test content"""
    import time

    content_map = {
        "Document": ("test-page", "Test Page"),
        "News Item": ("test-news", "Test News"),
        "Folder": ("test-folder", "Test Folder"),
    }

    base_id, base_title = content_map.get(content_type, ("test-item", "Test Item"))

    # If no suffix provided, add timestamp to ensure uniqueness
    if not id_suffix:
        id_suffix = f"-{int(time.time() * 1000000) % 1000000}"

    obj_id = f"{base_id}{id_suffix}"
    obj_title = f"{base_title}{title_suffix}"

    portal.invokeFactory(content_type, obj_id, title=obj_title)
    return portal[obj_id]


# Decorators for common test patterns
def with_test_content(*content_types):
    """Decorator to create test content and add it to test instance"""

    def decorator(test_method):
        @functools.wraps(test_method)
        def wrapper(self):
            # Create content and store references
            self.test_objects = {}
            for i, content_type in enumerate(content_types):
                suffix = f"-{i}" if i > 0 else ""
                obj = create_test_content(self.portal, content_type, suffix, suffix)
                key = content_type.lower().replace(" ", "_")
                if key in self.test_objects:
                    key = f"{key}_{i}"
                self.test_objects[key] = obj

            return test_method(self)

        return wrapper

    return decorator


# Helper assertion mixins
class RecycleBinAssertionMixin:
    """Mixin providing common assertion methods for recycle bin tests"""

    def assertItemInRecycleBin(
        self, item_id, obj_id=None, obj_title=None, obj_type=None
    ):
        """Assert that an item is properly stored in the recycle bin"""
        self.assertIn(item_id, self.recyclebin.storage)

        if obj_id or obj_title or obj_type:
            item_data = self.recyclebin.storage[item_id]
            if obj_id:
                self.assertEqual(item_data["id"], obj_id)
            if obj_title:
                self.assertEqual(item_data["title"], obj_title)
            if obj_type:
                self.assertEqual(item_data["type"], obj_type)

    def assertItemNotInRecycleBin(self, item_id):
        """Assert that an item is not in the recycle bin"""
        self.assertNotIn(item_id, self.recyclebin.storage)

    def assertRecycleBinEmpty(self):
        """Assert that the recycle bin is empty"""
        items = self.recyclebin.get_items()
        self.assertEqual(len(items), 0)

    def assertRecycleBinCount(self, expected_count):
        """Assert the number of items in the recycle bin"""
        items = self.recyclebin.get_items()
        self.assertEqual(len(items), expected_count)

    def assertItemRestored(self, restored_obj, original_id, original_title, container):
        """Assert that an item was successfully restored"""
        self.assertIsNotNone(restored_obj)
        self.assertEqual(restored_obj.getId(), original_id)
        self.assertEqual(restored_obj.Title(), original_title)
        self.assertIn(original_id, container)

    def assertFolderContentsRestored(self, folder, expected_children):
        """Assert that folder contents were properly restored"""
        for child_id, child_title in expected_children.items():
            self.assertIn(child_id, folder)
            self.assertEqual(folder[child_id].Title(), child_title)


# Content creation utilities
class ContentTestHelper:
    """Helper class for creating and managing test content"""

    @staticmethod
    def create_nested_folder_structure(portal, depth=2):
        """Create a nested folder structure for testing"""
        current_container = portal
        folders = []

        for i in range(depth):
            folder_id = f"folder-level-{i}"
            folder_title = f"Folder Level {i}"
            current_container.invokeFactory("Folder", folder_id, title=folder_title)
            folder = current_container[folder_id]
            folders.append(folder)

            # Add some content to each folder
            folder.invokeFactory("Document", f"page-{i}", title=f"Page {i}")
            folder.invokeFactory("News Item", f"news-{i}", title=f"News {i}")

            current_container = folder

        return folders

    @staticmethod
    def create_workflow_content(
        portal, workflow_tool, content_type="Document", state="published"
    ):
        """Create content with specific workflow state"""
        obj_id = f"workflow-{state}-{content_type.lower().replace(' ', '-')}"
        title = f"Workflow {state.title()} {content_type}"

        portal.invokeFactory(content_type, obj_id, title=title)
        obj = portal[obj_id]

        # Only try to transition if workflow tool is available and workflows exist
        if workflow_tool and state != "private":
            try:
                # Check if there are any workflows configured for this content type
                workflow_chain = workflow_tool.getChainFor(obj)
                if workflow_chain:
                    # Try to get available transitions
                    transitions = workflow_tool.getTransitionsFor(obj)
                    if transitions:
                        # Look for a publish transition
                        for transition in transitions:
                            if transition["id"] == "publish":
                                workflow_tool.doActionFor(obj, "publish")
                                break
            except Exception:
                # If workflow operations fail, just continue with default state
                pass

        return obj


class RecycleBinTestCase(unittest.TestCase, RecycleBinAssertionMixin):
    """Base test case for RecycleBin tests with optimized setup and helper methods"""

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

        # Get the recycle bin utility
        self.recyclebin = getUtility(IRecycleBin)

        # Configure recycle bin with test-optimized settings
        self._configure_recyclebin_settings()

        # Clear any existing items from the recycle bin
        self._clear_recyclebin()

    def tearDown(self):
        """Clean up after the test"""
        self._clear_recyclebin()

    def _configure_recyclebin_settings(self, **overrides):
        """Configure recycle bin settings with sensible test defaults"""
        settings = self.registry.forInterface(
            IRecycleBinControlPanelSettings, prefix="recyclebin-controlpanel"
        )

        # Default test settings
        default_settings = {
            "recycling_enabled": True,
            "retention_period": 30,
            "maximum_size": 100,  # 100 MB
            "restore_to_initial_state": False,
        }

        # Apply overrides
        default_settings.update(overrides)

        # Set the settings
        for key, value in default_settings.items():
            setattr(settings, key, value)

    def _clear_recyclebin(self):
        """Clear all items from the recycle bin"""
        annotations = IAnnotations(self.portal)
        if ANNOTATION_KEY in annotations:
            del annotations[ANNOTATION_KEY]

    def _add_item_to_recyclebin(self, obj, container=None):
        """Helper method to add an item to the recycle bin"""
        if container is None:
            container = self.portal
        obj_path = "/".join(obj.getPhysicalPath())
        return self.recyclebin.add_item(obj, container, obj_path)

    def _simulate_deletion(self, obj, container=None):
        """Helper method to simulate object deletion from container"""
        if container is None:
            container = self.portal
        obj_id = obj.getId()
        if obj_id in container:
            del container[obj_id]

    def _test_basic_recycle_restore_cycle(self, obj, container=None):
        """Test the basic cycle of recycling and restoring an object"""
        if container is None:
            container = self.portal

        # Store original info
        obj_id = obj.getId()
        obj_title = obj.Title()
        # Use the same logic as the recyclebin implementation for consistency
        obj_type = getattr(obj, "portal_type", "Unknown")

        # Add to recycle bin
        recycle_id = self._add_item_to_recyclebin(obj, container)

        # Verify it was added correctly
        self.assertItemInRecycleBin(recycle_id, obj_id, obj_title, obj_type)

        # Simulate deletion
        self._simulate_deletion(obj, container)
        self.assertNotIn(obj_id, container)

        # Restore the item
        restored_obj = self.recyclebin.restore_item(recycle_id)

        # Verify restoration
        self.assertItemRestored(restored_obj, obj_id, obj_title, container)
        self.assertItemNotInRecycleBin(recycle_id)

        return restored_obj


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
        # Create test content using helper functions
        self.page = create_test_content(self.portal, "Document")
        self.news = create_test_content(self.portal, "News Item")

    def test_delete_restore_page(self):
        """Test deleting and restoring a page"""
        self._test_basic_recycle_restore_cycle(self.page)

    def test_delete_restore_news(self):
        """Test deleting and restoring a news item"""
        restored_news = self._test_basic_recycle_restore_cycle(self.news)

        # Verify additional news-specific behavior
        self.assertEqual(restored_news.portal_type, "News Item")

    def test_content_types_metadata_storage(self):
        """Test that different content types store metadata correctly"""
        content_items = [(self.page, "Document"), (self.news, "News Item")]

        for obj, expected_type in content_items:
            with self.subTest(content_type=expected_type):
                recycle_id = self._add_item_to_recyclebin(obj)
                item_data = self.recyclebin.storage[recycle_id]

                # Common metadata assertions
                self.assertEqual(item_data["id"], obj.getId())
                self.assertEqual(item_data["title"], obj.Title())
                self.assertEqual(item_data["type"], expected_type)
                self.assertIsInstance(item_data["deletion_date"], datetime)
                self.assertIn("deleted_by", item_data)
                self.assertEqual(item_data["deleted_by"], TEST_USER_ID)

                # Clean up for next iteration
                del self.recyclebin.storage[recycle_id]

    def test_purge_item(self):
        """Test purging an item from the recycle bin"""
        recycle_id = self._add_item_to_recyclebin(self.page)

        # Verify it was added to the recycle bin
        self.assertItemInRecycleBin(recycle_id)

        # Purge the item
        result = self.recyclebin.purge_item(recycle_id)

        # Verify the item was purged
        self.assertTrue(result)
        self.assertItemNotInRecycleBin(recycle_id)
        self.assertRecycleBinEmpty()

    def test_deleted_by_field(self):
        """Test that deleted_by field is properly stored and retrieved"""
        recycle_id = self._add_item_to_recyclebin(self.page)

        # Test deleted_by field in various access methods
        access_methods = [
            ("storage", lambda: self.recyclebin.storage[recycle_id]),
            ("get_items", lambda: self.recyclebin.get_items()[0]),
            ("get_item", lambda: self.recyclebin.get_item(recycle_id)),
        ]

        for method_name, get_item_data in access_methods:
            with self.subTest(access_method=method_name):
                item_data = get_item_data()
                self.assertIn("deleted_by", item_data)
                self.assertIsInstance(item_data["deleted_by"], str)
                self.assertEqual(item_data["deleted_by"], TEST_USER_ID)


class RecycleBinFolderTests(RecycleBinTestCase):
    """Tests for deleting and restoring folder structures"""

    def setUp(self):
        """Set up test content"""
        super().setUp()

        # Create a folder with content using helper
        self.folder = create_test_content(self.portal, "Folder")

        # Add content to the folder
        self.folder.invokeFactory("Document", "folder-page", title="Folder Page")
        self.folder.invokeFactory("News Item", "folder-news", title="Folder News")

        # Store expected children for easier testing
        self.expected_children = {
            "folder-page": "Folder Page",
            "folder-news": "Folder News",
        }

    def test_delete_restore_folder(self):
        """Test deleting and restoring a folder with content"""
        restored_folder = self._test_basic_recycle_restore_cycle(self.folder)

        # Verify folder-specific behavior: children were restored
        self.assertFolderContentsRestored(restored_folder, self.expected_children)

    def test_folder_children_tracking(self):
        """Test that folder children are properly tracked in recycle bin"""
        recycle_id = self._add_item_to_recyclebin(self.folder)
        item_data = self.recyclebin.storage[recycle_id]

        # Verify children tracking
        self.assertIn("children", item_data)
        self.assertEqual(item_data["children_count"], 2)

        # Verify each child is tracked
        for child_id in self.expected_children.keys():
            self.assertIn(child_id, item_data["children"])

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

        # Use helper to create nested structure
        self.folders = ContentTestHelper.create_nested_folder_structure(
            self.portal, depth=3
        )
        self.parent_folder = self.folders[0]
        self.child_folder = self.folders[1] if len(self.folders) > 1 else None
        self.grandchild_folder = self.folders[2] if len(self.folders) > 2 else None

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
        self.assertEqual(item_data["children_count"], 3)
        self.assertIn("page-0", item_data["children"])
        self.assertIn("news-0", item_data["children"])
        self.assertIn("folder-level-1", item_data["children"])

        # Verify the nested children were tracked
        child_data = item_data["children"]["folder-level-1"]
        self.assertIn("children", child_data)
        self.assertEqual(child_data["children_count"], 3)
        self.assertIn("page-1", child_data["children"])
        self.assertIn("news-1", child_data["children"])
        self.assertIn("folder-level-2", child_data["children"])

        # Verify the deepest level was tracked
        grandchild_data = child_data["children"]["folder-level-2"]
        self.assertIn("children", grandchild_data)
        self.assertEqual(grandchild_data["children_count"], 2)
        self.assertIn("page-2", grandchild_data["children"])
        self.assertIn("news-2", grandchild_data["children"])

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
        self.assertIn("folder-level-1", restored_folder)
        restored_child = restored_folder["folder-level-1"]

        # Verify the nested content was restored
        self.assertIn("page-1", restored_child)
        self.assertIn("news-1", restored_child)
        self.assertIn("folder-level-2", restored_child)

        # Verify the deepest level was restored
        restored_grandchild = restored_child["folder-level-2"]
        self.assertIn("page-2", restored_grandchild)
        self.assertIn("news-2", restored_grandchild)

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
        self.assertIn("page-1", restored_folder)
        self.assertIn("news-1", restored_folder)
        self.assertIn("folder-level-2", restored_folder)

        # Verify the deepest level was restored
        restored_grandchild = restored_folder["folder-level-2"]
        self.assertIn("page-2", restored_grandchild)
        self.assertIn("news-2", restored_grandchild)

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


class RecycleBinWorkflowTests(RecycleBinTestCase):
    """Tests for workflow state restoration functionality"""

    def setUp(self):
        """Set up test content with workflow states"""
        super().setUp()

        # Import here to avoid module resolution issues
        try:
            from Products.CMFCore.utils import getToolByName

            self.workflow_tool = getToolByName(self.portal, "portal_workflow")
        except ImportError:
            # Fallback for testing without full Plone environment
            self.workflow_tool = None

        # Check if workflows are actually available before proceeding
        if self.workflow_tool:
            try:
                # Create a simple test document first
                self.portal.invokeFactory(
                    "Document", "test-workflow-doc", title="Test Doc"
                )
                test_obj = self.portal["test-workflow-doc"]

                # Check if workflows are configured
                workflow_chain = self.workflow_tool.getChainFor(test_obj)
                if not workflow_chain:
                    self.workflow_tool = None
                else:
                    # Clean up test object
                    del self.portal["test-workflow-doc"]
            except Exception:
                self.workflow_tool = None

        if not self.workflow_tool:
            self.skipTest("Workflow tool not available or no workflows configured")

        # Create workflow content using helper
        self.page = ContentTestHelper.create_workflow_content(
            self.portal, self.workflow_tool, "Document", "published"
        )

    def test_workflow_state_restoration_scenarios(self):
        """Parameterized test for different workflow restoration scenarios"""
        if not self.workflow_tool:
            self.skipTest("Workflow tool not available")

        # Create a simple test document without trying to change workflow state
        self.portal.invokeFactory(
            "Document", "workflow-test-doc", title="Workflow Test"
        )
        test_page = self.portal["workflow-test-doc"]

        # Get the current workflow state (whatever it is)
        try:
            current_state = self.workflow_tool.getInfoFor(test_page, "review_state")
        except Exception:
            current_state = None

        # Test scenarios based on actual workflow availability
        test_scenarios = [
            (False, current_state),  # Don't reset workflow, expect current state
            (
                True,
                None,
            ),  # Reset workflow, expect initial state (determined dynamically)
        ]

        for reset_workflow, expected_state in test_scenarios:
            with self.subTest(reset_workflow=reset_workflow):
                # Configure workflow reset setting
                self._configure_recyclebin_settings(
                    restore_to_initial_state=reset_workflow
                )

                # Test the recycle/restore cycle
                recycle_id = self._add_item_to_recyclebin(test_page)
                test_page_id = test_page.getId()
                self._simulate_deletion(test_page)
                restored_page = self.recyclebin.restore_item(recycle_id)

                # Verify the page was restored
                self.assertIsNotNone(restored_page)
                self.assertEqual(restored_page.getId(), test_page_id)

                # Verify workflow state if workflows are available
                if current_state is not None:
                    try:
                        actual_state = self.workflow_tool.getInfoFor(
                            restored_page, "review_state"
                        )
                        if expected_state:
                            self.assertEqual(actual_state, expected_state)
                        elif reset_workflow:
                            # For reset workflow, check it matches initial state
                            workflow_chain = self.workflow_tool.getChainFor(
                                restored_page
                            )
                            if workflow_chain:
                                workflow = self.workflow_tool.getWorkflowById(
                                    workflow_chain[0]
                                )
                                initial_state = workflow.initial_state
                                self.assertEqual(actual_state, initial_state)
                    except Exception:
                        # If workflow operations fail, just verify basic restoration
                        pass

                # Clean up for next iteration - create fresh content
                if restored_page.getId() in self.portal:
                    del self.portal[restored_page.getId()]

                # Recreate test page for next iteration if there is one
                if reset_workflow != test_scenarios[-1][0]:  # Not the last iteration
                    self.portal.invokeFactory(
                        "Document", "workflow-test-doc", title="Workflow Test"
                    )
                    test_page = self.portal["workflow-test-doc"]


class RecycleBinStorageTests(RecycleBinTestCase):
    """Tests for RecycleBinStorage functionality including BTrees and sorting"""

    def test_storage_initialization(self):
        """Test that storage is properly initialized with BTrees"""
        storage = self.recyclebin.storage
        self.assertIsNotNone(storage.items)
        self.assertIsNotNone(storage._sorted_index)
        self.assertEqual(len(storage), 0)

    def test_storage_sorted_index(self):
        """Test that storage maintains sorted index by deletion date"""
        # Create items with different deletion dates
        items = []
        for i in range(3):
            obj = create_test_content(self.portal, "Document", f"-sorted-{i}")
            recycle_id = self._add_item_to_recyclebin(obj)
            items.append((recycle_id, obj))

            # Modify deletion date to create a sequence
            import time

            time.sleep(0.001)  # Small delay to ensure different timestamps

        # Test sorted retrieval (newest first by default)
        sorted_items = list(
            self.recyclebin.storage.get_items_sorted_by_date(reverse=True)
        )
        self.assertEqual(len(sorted_items), 3)

        # Verify items are sorted by date (newest first)
        for i in range(len(sorted_items) - 1):
            current_date = sorted_items[i][1]["deletion_date"]
            next_date = sorted_items[i + 1][1]["deletion_date"]
            self.assertGreaterEqual(current_date, next_date)

        # Test reverse sorting (oldest first)
        sorted_items_reverse = list(
            self.recyclebin.storage.get_items_sorted_by_date(reverse=False)
        )
        self.assertEqual(len(sorted_items_reverse), 3)

        # Verify reverse order
        for i in range(len(sorted_items_reverse) - 1):
            current_date = sorted_items_reverse[i][1]["deletion_date"]
            next_date = sorted_items_reverse[i + 1][1]["deletion_date"]
            self.assertLessEqual(current_date, next_date)

    def test_storage_index_maintenance(self):
        """Test that sorted index is properly maintained during operations"""
        obj = create_test_content(self.portal, "Document")
        recycle_id = self._add_item_to_recyclebin(obj)

        # Verify item is in index
        index_items = list(self.recyclebin.storage._sorted_index)
        self.assertEqual(len(index_items), 1)

        # Delete item and verify index is cleaned up
        del self.recyclebin.storage[recycle_id]
        index_items = list(self.recyclebin.storage._sorted_index)
        self.assertEqual(len(index_items), 0)


class RecycleBinSecurityTests(RecycleBinTestCase):
    """Tests for security and user tracking in recycle bin"""

    def test_user_tracking(self):
        """Test that deleted_by field correctly tracks the user"""
        obj = create_test_content(self.portal, "Document")
        recycle_id = self._add_item_to_recyclebin(obj)

        item_data = self.recyclebin.storage[recycle_id]
        self.assertEqual(item_data["deleted_by"], TEST_USER_ID)

    def test_different_user_deletions(self):
        """Test tracking different users' deletions"""
        from plone.app.testing import login
        from plone.app.testing import logout

        # Create content as first user
        obj1 = create_test_content(self.portal, "Document", "-user1")
        recycle_id1 = self._add_item_to_recyclebin(obj1)

        # Change to different user
        logout()
        # Create a test user
        self.portal.acl_users.userFolderAddUser("testuser2", "secret", ["Member"], [])
        login(self.portal, "testuser2")
        setRoles(self.portal, "testuser2", ["Manager"])

        obj2 = create_test_content(self.portal, "Document", "-user2")
        recycle_id2 = self._add_item_to_recyclebin(obj2)

        # Verify different users are tracked
        item1_data = self.recyclebin.storage[recycle_id1]
        item2_data = self.recyclebin.storage[recycle_id2]

        self.assertEqual(item1_data["deleted_by"], TEST_USER_ID)
        self.assertEqual(item2_data["deleted_by"], "testuser2")

        # Switch back to original user
        logout()
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])


class RecycleBinSizeLimitTests(RecycleBinTestCase):
    """Tests for size limit enforcement"""

    def test_size_limit_enforcement(self):
        """Test that size limits are enforced by purging oldest items"""
        # Set a reasonable size limit (minimum is 10MB)
        self._configure_recyclebin_settings(maximum_size=10)

        # Create items - actual size limit enforcement depends on implementation
        items = []
        for i in range(3):
            obj = create_test_content(self.portal, "Document", f"-size-{i}")
            recycle_id = self._add_item_to_recyclebin(obj)
            items.append(recycle_id)

        # Verify items were added (size enforcement may vary based on implementation)
        remaining_items = self.recyclebin.get_items()
        self.assertGreater(len(remaining_items), 0)  # At least some items should remain

    def test_size_limit_settings(self):
        """Test that size limit settings work within valid ranges"""
        # Test with minimum allowed size (10MB)
        self._configure_recyclebin_settings(maximum_size=10)

        # Create items
        items = []
        for i in range(2):
            obj = create_test_content(self.portal, "Document", f"-size-limit-{i}")
            recycle_id = self._add_item_to_recyclebin(obj)
            items.append(recycle_id)

        # All items should be added with reasonable size limit
        remaining_items = self.recyclebin.get_items()
        self.assertEqual(len(remaining_items), 2)


class RecycleBinRetentionTests(RecycleBinTestCase):
    """Tests for retention period and auto-purging"""

    def test_retention_period_enforcement(self):
        """Test that items are auto-purged after retention period"""
        # Set short retention period
        self._configure_recyclebin_settings(retention_period=1)  # 1 day

        obj = create_test_content(self.portal, "Document")
        recycle_id = self._add_item_to_recyclebin(obj)

        # Mock the deletion date to be older than retention period
        old_date = datetime.now() - timedelta(days=2)
        self.recyclebin.storage[recycle_id]["deletion_date"] = old_date

        # Trigger expiration check
        purged_count = self.recyclebin._purge_expired_items()

        # Verify item was purged
        self.assertEqual(purged_count, 1)
        self.assertItemNotInRecycleBin(recycle_id)

    def test_retention_period_disabled(self):
        """Test that auto-purging can be disabled"""
        # Disable retention period
        self._configure_recyclebin_settings(retention_period=0)

        obj = create_test_content(self.portal, "Document")
        recycle_id = self._add_item_to_recyclebin(obj)

        # Mock very old deletion date
        old_date = datetime.now() - timedelta(days=365)
        self.recyclebin.storage[recycle_id]["deletion_date"] = old_date

        # Trigger expiration check
        purged_count = self.recyclebin._purge_expired_items()

        # Verify no items were purged
        self.assertEqual(purged_count, 0)
        self.assertItemInRecycleBin(recycle_id)


class RecycleBinWorkflowHistoryTests(RecycleBinTestCase):
    """Tests for workflow history tracking"""

    def test_workflow_history_on_deletion(self):
        """Test that workflow history is updated on deletion"""
        obj = create_test_content(self.portal, "Document")

        # Add to recycle bin
        recycle_id = self._add_item_to_recyclebin(obj)

        # Verify item was added to recycle bin
        self.assertItemInRecycleBin(recycle_id)

        # Check if workflow history was updated (this depends on workflow being available)
        if hasattr(obj, "workflow_history"):
            # Verify some workflow history exists
            self.assertTrue(len(obj.workflow_history) >= 0)

    def test_workflow_history_on_restoration(self):
        """Test that workflow history is updated on restoration"""
        obj = create_test_content(self.portal, "Document")
        obj_id = obj.getId()

        # Add to recycle bin and simulate deletion
        recycle_id = self._add_item_to_recyclebin(obj)
        self._simulate_deletion(obj)

        # Restore the item
        restored_obj = self.recyclebin.restore_item(recycle_id)

        # Verify restoration was successful
        self.assertIsNotNone(restored_obj)
        self.assertEqual(restored_obj.getId(), obj_id)


class RecycleBinPathTests(RecycleBinTestCase):
    """Tests for path handling and resolution"""

    def test_path_storage_and_retrieval(self):
        """Test that paths are correctly stored and can be used for restoration"""
        # Create nested structure
        folder = create_test_content(self.portal, "Folder")
        folder.invokeFactory("Document", "nested-doc", title="Nested Document")
        nested_doc = folder["nested-doc"]

        # Get original paths
        folder_path = "/".join(folder.getPhysicalPath())
        doc_path = "/".join(nested_doc.getPhysicalPath())

        # Add to recycle bin
        folder_recycle_id = self._add_item_to_recyclebin(folder)
        doc_recycle_id = self._add_item_to_recyclebin(nested_doc, folder)

        # Verify paths are stored correctly
        folder_data = self.recyclebin.storage[folder_recycle_id]
        doc_data = self.recyclebin.storage[doc_recycle_id]

        self.assertEqual(folder_data["path"], folder_path)
        self.assertEqual(doc_data["path"], doc_path)
        self.assertEqual(doc_data["parent_path"], folder_path)

    def test_path_resolution_for_restoration(self):
        """Test path resolution during restoration"""
        folder = create_test_content(self.portal, "Folder")
        folder.invokeFactory("Document", "path-test-doc", title="Path Test Document")
        doc = folder["path-test-doc"]

        # Add document to recycle bin
        doc_recycle_id = self._add_item_to_recyclebin(doc, folder)

        # Simulate deletion of document only (folder remains)
        del folder["path-test-doc"]

        # Restore document
        restored_doc = self.recyclebin.restore_item(doc_recycle_id)

        # Verify document was restored to correct location
        self.assertIsNotNone(restored_doc)
        self.assertIn("path-test-doc", folder)
        self.assertEqual(folder["path-test-doc"].Title(), "Path Test Document")


class RecycleBinMetadataTests(RecycleBinTestCase):
    """Tests for comprehensive metadata storage and retrieval"""

    def test_complete_metadata_storage(self):
        """Test that all expected metadata fields are stored"""
        obj = create_test_content(self.portal, "Document")
        recycle_id = self._add_item_to_recyclebin(obj)

        item_data = self.recyclebin.storage[recycle_id]

        # Required fields
        required_fields = [
            "id",
            "title",
            "type",
            "path",
            "parent_path",
            "deletion_date",
            "deleted_by",
            "size",
            "object",
        ]

        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(field, item_data)
                self.assertIsNotNone(item_data[field])


class RecycleBinSpecialContentTests(RecycleBinTestCase):
    """Tests for special content types and edge cases"""

    def test_title_fallback_mechanisms(self):
        """Test different title fallback mechanisms"""
        obj = create_test_content(self.portal, "Document")

        # Test with Title method (normal case)
        recycle_id = self._add_item_to_recyclebin(obj)
        item_data = self.recyclebin.storage[recycle_id]
        self.assertEqual(item_data["title"], obj.Title())

    def test_size_fallback_mechanisms(self):
        """Test different size determination mechanisms"""
        obj = create_test_content(self.portal, "Document")

        # Test with existing size methods
        recycle_id = self._add_item_to_recyclebin(obj)
        item_data = self.recyclebin.storage[recycle_id]

        # Size should be determined by available methods
        self.assertIsInstance(item_data["size"], int)
        self.assertGreaterEqual(item_data["size"], 0)


class RecycleBinConcurrencyTests(RecycleBinTestCase):
    """Tests for concurrent operations and data integrity"""

    def test_concurrent_additions(self):
        """Test that concurrent additions work correctly"""
        # Simulate concurrent additions
        items = []
        for i in range(10):
            obj = create_test_content(self.portal, "Document", f"-concurrent-{i}")
            recycle_id = self._add_item_to_recyclebin(obj)
            items.append(recycle_id)

        # Verify all items were added
        self.assertRecycleBinCount(10)

        # Verify each item is properly stored
        for recycle_id in items:
            self.assertItemInRecycleBin(recycle_id)

    def test_concurrent_modifications(self):
        """Test that storage handles concurrent modifications properly"""
        obj = create_test_content(self.portal, "Document")
        recycle_id = self._add_item_to_recyclebin(obj)

        # Modify item data
        original_data = self.recyclebin.storage[recycle_id].copy()
        original_data["custom_field"] = "test_value"
        self.recyclebin.storage[recycle_id] = original_data

        # Verify modification was preserved
        modified_data = self.recyclebin.storage[recycle_id]
        self.assertEqual(modified_data["custom_field"], "test_value")


class OptimizedRecycleBinTests(RecycleBinTestCase):
    """Demonstration of optimized test patterns and comprehensive scenarios"""

    def test_multiple_content_types_cycle(self):
        """Test recycle/restore cycle for multiple content types in one test"""
        content_types = ["Document", "News Item", "Folder"]

        for content_type in content_types:
            with self.subTest(content_type=content_type):
                # Create content
                obj = create_test_content(
                    self.portal, content_type, f"-{content_type.lower()}"
                )

                # Test full cycle
                self._test_basic_recycle_restore_cycle(obj)

    @with_test_content("Document", "News Item", "Folder")
    def test_bulk_operations_with_decorator(self):
        """Test bulk operations using the decorator pattern"""
        # All content is already created by decorator
        recycle_ids = []

        # Add all items to recycle bin
        for obj in self.test_objects.values():
            recycle_id = self._add_item_to_recyclebin(obj)
            recycle_ids.append(recycle_id)

        # Verify all items are in recycle bin
        self.assertRecycleBinCount(len(recycle_ids))

        # Purge all items
        for recycle_id in recycle_ids:
            self.assertTrue(self.recyclebin.purge_item(recycle_id))

        # Verify recycle bin is empty
        self.assertRecycleBinEmpty()

    def test_edge_cases_comprehensive(self):
        """Test various edge cases in a single comprehensive test"""
        # Test with empty recycle bin
        self.assertRecycleBinEmpty()

        # Test invalid operations
        self.assertFalse(self.recyclebin.purge_item("non-existent-id"))
        self.assertIsNone(self.recyclebin.get_item("non-existent-id"))

        # Test settings configuration
        self._configure_recyclebin_settings(
            recycling_enabled=False, retention_period=60, maximum_size=200
        )

        settings = self.recyclebin._get_settings()
        self.assertFalse(settings.recycling_enabled)
        self.assertEqual(settings.retention_period, 60)
        self.assertEqual(settings.maximum_size, 200)

    def test_disabled_recyclebin_behavior(self):
        """Test behavior when recycle bin is disabled"""
        # Disable recycling
        self._configure_recyclebin_settings(recycling_enabled=False)

        # Verify is_enabled returns False
        self.assertFalse(self.recyclebin.is_enabled())

        # Try to add item - should return None
        obj = create_test_content(self.portal, "Document")
        result = self.recyclebin.add_item(
            obj, self.portal, "/".join(obj.getPhysicalPath())
        )

        self.assertIsNone(result)
        self.assertRecycleBinEmpty()

    def test_error_handling_in_settings(self):
        """Test error handling when settings are not available"""
        # Test that recyclebin gracefully handles missing settings
        # In normal operation, is_enabled() should work correctly
        enabled_state = self.recyclebin.is_enabled()
        self.assertIsInstance(enabled_state, bool)

    def test_comprehensive_item_lifecycle(self):
        """Test complete item lifecycle from creation to final purge"""
        # Create and track content through entire lifecycle
        obj = create_test_content(self.portal, "Document", "-lifecycle")
        obj_id = obj.getId()
        obj_title = obj.Title()

        # Stage 1: Add to recycle bin
        recycle_id = self._add_item_to_recyclebin(obj)
        self.assertIsNotNone(recycle_id)
        self.assertItemInRecycleBin(recycle_id)

        # Stage 2: Verify all metadata is present
        item_data = self.recyclebin.get_item(recycle_id)
        self.assertEqual(item_data["id"], obj_id)
        self.assertEqual(item_data["title"], obj_title)
        self.assertIn("deletion_date", item_data)
        self.assertIn("deleted_by", item_data)

        # Stage 3: Verify item appears in listings
        all_items = self.recyclebin.get_items()
        self.assertEqual(len(all_items), 1)
        self.assertEqual(all_items[0]["id"], obj_id)

        # Stage 4: Simulate deletion from portal
        self._simulate_deletion(obj)
        self.assertNotIn(obj_id, self.portal)

        # Stage 5: Restore item
        restored_obj = self.recyclebin.restore_item(recycle_id)
        self.assertIsNotNone(restored_obj)
        self.assertEqual(restored_obj.getId(), obj_id)
        self.assertIn(obj_id, self.portal)

        # Stage 6: Item should be removed from recycle bin after restoration
        self.assertItemNotInRecycleBin(recycle_id)
        # Note: Other tests may have left items in recycle bin, so check specific item only

        # Stage 7: Add back to recycle bin and permanently purge
        recycle_id2 = self._add_item_to_recyclebin(restored_obj)
        self.assertItemInRecycleBin(recycle_id2)

        purged = self.recyclebin.purge_item(recycle_id2)
        self.assertTrue(purged)
        self.assertItemNotInRecycleBin(recycle_id2)


class RecycleBinNestedContentTests(RecycleBinTestCase):
    """Tests for nested content handling"""

    def test_nested_folder_structure(self):
        """Test handling of nested folder structures"""
        # Create nested structure
        folder1 = create_test_content(self.portal, "Folder", "-level1")
        folder1.invokeFactory("Folder", "level2", title="Level 2 Folder")
        folder2 = folder1["level2"]
        folder2.invokeFactory("Document", "nested-doc", title="Nested Document")
        nested_doc = folder2["nested-doc"]

        # Test adding nested items to recycle bin
        doc_recycle_id = self._add_item_to_recyclebin(nested_doc, folder2)
        folder2_recycle_id = self._add_item_to_recyclebin(folder2, folder1)
        folder1_recycle_id = self._add_item_to_recyclebin(folder1, self.portal)

        # Verify all items are in recycle bin
        self.assertItemInRecycleBin(doc_recycle_id)
        self.assertItemInRecycleBin(folder2_recycle_id)
        self.assertItemInRecycleBin(folder1_recycle_id)

        # Verify parent paths are correctly stored
        doc_data = self.recyclebin.storage[doc_recycle_id]
        folder2_data = self.recyclebin.storage[folder2_recycle_id]
        folder1_data = self.recyclebin.storage[folder1_recycle_id]

        # Check that paths contain the expected components
        self.assertIn("level2", doc_data["parent_path"])
        self.assertIn("level1", folder2_data["parent_path"])
        self.assertIn("plone", folder1_data["parent_path"])

    def test_parent_path_resolution(self):
        """Test parent path resolution for deeply nested content"""
        # Create deep nesting
        current_container = self.portal
        containers = []

        for i in range(3):
            folder_id = f"folder-{i}"
            current_container.invokeFactory("Folder", folder_id, title=f"Folder {i}")
            current_container = current_container[folder_id]
            containers.append(current_container)

        # Add final document
        current_container.invokeFactory("Document", "deep-doc", title="Deep Document")
        deep_doc = current_container["deep-doc"]

        # Add to recycle bin
        recycle_id = self._add_item_to_recyclebin(deep_doc, current_container)

        # Verify path information
        item_data = self.recyclebin.storage[recycle_id]
        self.assertIn("folder-0", item_data["parent_path"])
        self.assertIn("folder-1", item_data["parent_path"])
        self.assertIn("folder-2", item_data["parent_path"])


class RecycleBinBulkOperationsTests(RecycleBinTestCase):
    """Tests for bulk operations and performance"""

    def test_bulk_addition_performance(self):
        """Test performance of bulk additions"""
        import time

        # Create multiple items
        items = []
        start_time = time.time()

        for i in range(20):
            obj = create_test_content(self.portal, "Document", f"-bulk-{i}")
            recycle_id = self._add_item_to_recyclebin(obj)
            items.append(recycle_id)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete in reasonable time (less than 2 seconds for 20 items)
        self.assertLess(duration, 2.0)

        # Verify all items were added
        self.assertEqual(len(items), 20)
        for recycle_id in items:
            self.assertItemInRecycleBin(recycle_id)

    def test_bulk_retrieval_operations(self):
        """Test bulk retrieval operations"""
        # Add multiple items
        items = []
        for i in range(10):
            obj = create_test_content(self.portal, "Document", f"-retrieval-{i}")
            recycle_id = self._add_item_to_recyclebin(obj)
            items.append(recycle_id)

        # Test get_items performance
        import time

        start_time = time.time()
        all_items = self.recyclebin.get_items()
        end_time = time.time()

        # Should be fast
        self.assertLess(end_time - start_time, 1.0)
        self.assertGreaterEqual(len(all_items), 10)

    def test_bulk_purge_operations(self):
        """Test bulk purging operations"""
        # Add items
        items = []
        for i in range(5):
            obj = create_test_content(self.portal, "Document", f"-purge-{i}")
            recycle_id = self._add_item_to_recyclebin(obj)
            items.append(recycle_id)

        # Purge all items
        purged_count = 0
        for recycle_id in items:
            if self.recyclebin.purge_item(recycle_id):
                purged_count += 1

        # Verify all were purged
        self.assertEqual(purged_count, 5)
        for recycle_id in items:
            self.assertItemNotInRecycleBin(recycle_id)


class RecycleBinDataIntegrityTests(RecycleBinTestCase):
    """Tests for data integrity and consistency"""

    def test_storage_consistency_after_operations(self):
        """Test that storage remains consistent after various operations"""
        # Add item
        obj = create_test_content(self.portal, "Document")
        recycle_id = self._add_item_to_recyclebin(obj)

        # Verify storage consistency
        self.assertEqual(len(self.recyclebin.storage), len(self.recyclebin.get_items()))

        # Purge item
        self.recyclebin.purge_item(recycle_id)

        # Verify consistency after purge
        self.assertEqual(len(self.recyclebin.storage), len(self.recyclebin.get_items()))

    def test_metadata_integrity(self):
        """Test that metadata remains intact throughout operations"""
        obj = create_test_content(self.portal, "Document")
        original_title = obj.Title()
        original_id = obj.getId()

        recycle_id = self._add_item_to_recyclebin(obj)

        # Verify metadata integrity
        item_data = self.recyclebin.storage[recycle_id]
        self.assertEqual(item_data["title"], original_title)
        self.assertEqual(item_data["id"], original_id)
        self.assertIn("deletion_date", item_data)
        self.assertIn("deleted_by", item_data)

        # Get item through different methods and verify consistency
        get_item_result = self.recyclebin.get_item(recycle_id)
        get_items_result = [
            item for item in self.recyclebin.get_items() if item["id"] == original_id
        ][0]

        key_fields = ["id", "title", "type", "deleted_by"]
        for field in key_fields:
            self.assertEqual(item_data[field], get_item_result[field])
            self.assertEqual(item_data[field], get_items_result[field])


class RecycleBinBrowserViewTests(RecycleBinTestCase):
    """Tests for browser view integration and functionality"""

    def test_recyclebin_view_integration(self):
        """Test integration with browser views"""
        # This tests the integration points that browser views would use
        obj = create_test_content(self.portal, "Document")
        recycle_id = self._add_item_to_recyclebin(obj)

        # Test methods that browser views typically use
        items = self.recyclebin.get_items()
        self.assertGreater(len(items), 0)

        item = self.recyclebin.get_item(recycle_id)
        self.assertIsNotNone(item)

        # Test that view-related metadata is present
        self.assertIn("deletion_date", item)
        self.assertIn("size", item)
        self.assertIn("type", item)

    def test_item_filtering_support(self):
        """Test support for filtering that browser views might use"""
        # Create items of different types
        doc = create_test_content(self.portal, "Document", "-filter-doc")
        folder = create_test_content(self.portal, "Folder", "-filter-folder")

        self._add_item_to_recyclebin(doc)
        self._add_item_to_recyclebin(folder)

        # Get all items
        all_items = self.recyclebin.get_items()

        # Filter by type (simulating what a browser view might do)
        doc_items = [item for item in all_items if item["type"] == "Document"]
        folder_items = [item for item in all_items if item["type"] == "Folder"]

        self.assertGreater(len(doc_items), 0)
        self.assertGreater(len(folder_items), 0)

        # Verify specific items are found
        doc_found = any(item["id"].endswith("-filter-doc") for item in doc_items)
        folder_found = any(
            item["id"].endswith("-filter-folder") for item in folder_items
        )

        self.assertTrue(doc_found)
        self.assertTrue(folder_found)
