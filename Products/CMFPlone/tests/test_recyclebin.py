from datetime import datetime
from datetime import timedelta
from persistent.mapping import PersistentMapping
from Products.CMFPlone.recyclebin import ANNOTATION_KEY
from Products.CMFPlone.recyclebin import RecycleBin
from unittest.mock import Mock
from unittest.mock import patch

import unittest


class TestRecycleBin(unittest.TestCase):
    """Test the RecycleBin functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Mock site and annotations
        self.site = Mock()
        self.annotations = {}
        self.annotations_mock = Mock()
        self.annotations_mock.__getitem__ = lambda _, key: self.annotations.get(
            key, None
        )
        self.annotations_mock.__setitem__ = (
            lambda _, key, value: self.annotations.__setitem__(key, value)
        )
        self.annotations_mock.__contains__ = lambda _, key: key in self.annotations

        # Mock registry and settings
        self.settings_mock = Mock()
        self.settings_mock.recycling_enabled = True
        self.settings_mock.auto_purge = True
        self.settings_mock.retention_period = 30
        self.settings_mock.maximum_size = 100  # 100 MB

        self.registry_mock = Mock()
        self.registry_mock.forInterface.return_value = self.settings_mock

        # Create recycle bin instance
        self.recycle_bin = RecycleBin(self.site)

    def _setup_storage(self):
        """Initialize storage with test data"""
        self.storage = PersistentMapping()
        self.annotations[ANNOTATION_KEY] = self.storage

    @patch("Products.CMFPlone.recyclebin.IAnnotations")
    @patch("Products.CMFPlone.recyclebin.getUtility")
    def test_is_enabled(self, getUtility_mock, IAnnotations_mock):
        """Test checking if recycle bin is enabled"""
        # Configure mocks
        getUtility_mock.return_value = self.registry_mock

        # Test enabled
        result = self.recycle_bin.is_enabled()
        self.assertTrue(result)

        # Test disabled
        self.settings_mock.recycling_enabled = False
        result = self.recycle_bin.is_enabled()
        self.assertFalse(result)

        # Test exception handling
        getUtility_mock.side_effect = KeyError("Not found")
        result = self.recycle_bin.is_enabled()
        self.assertFalse(result)

    @patch("Products.CMFPlone.recyclebin.IAnnotations")
    @patch("Products.CMFPlone.recyclebin.getUtility")
    @patch("Products.CMFPlone.recyclebin.uuid")
    def test_add_item(self, uuid_mock, getUtility_mock, IAnnotations_mock):
        """Test adding an item to the recycle bin"""
        # Configure mocks
        test_uuid = "test-uuid-12345"
        uuid_mock.uuid4.return_value = test_uuid
        getUtility_mock.return_value = self.registry_mock
        IAnnotations_mock.return_value = self.annotations_mock

        # Setup storage
        self._setup_storage()

        # Create a mock deleted object
        deleted_obj = Mock()
        deleted_obj.getId.return_value = "test-document"
        deleted_obj.Title.return_value = "Test Document"
        deleted_obj.portal_type = "Document"
        deleted_obj.get_size = lambda: 1024

        # Create mock container
        container = Mock()
        container.getPhysicalPath.return_value = ["", "plone", "folder"]

        # Add item to recycle bin
        item_id = self.recycle_bin.add_item(
            deleted_obj, container, "/plone/folder/test-document"
        )

        # Verify item was added correctly
        self.assertEqual(item_id, test_uuid)
        self.assertIn(test_uuid, self.storage)
        item_data = self.storage[test_uuid]
        self.assertEqual(item_data["id"], "test-document")
        self.assertEqual(item_data["title"], "Test Document")
        self.assertEqual(item_data["type"], "Document")
        self.assertEqual(item_data["path"], "/plone/folder/test-document")
        self.assertEqual(item_data["parent_path"], "/plone/folder")
        self.assertEqual(item_data["size"], 1024)
        self.assertEqual(item_data["object"], deleted_obj)

        # Test when recycle bin is disabled
        self.settings_mock.recycling_enabled = False
        item_id = self.recycle_bin.add_item(deleted_obj, container, "/path")
        self.assertIsNone(item_id)

    @patch("Products.CMFPlone.recyclebin.IAnnotations")
    def test_get_items(self, IAnnotations_mock):
        """Test retrieving items from the recycle bin"""
        # Configure mocks
        IAnnotations_mock.return_value = self.annotations_mock

        # Setup storage with test data
        self._setup_storage()
        now = datetime.now()

        # Add test items with different dates
        self.storage["item1"] = {
            "id": "doc1",
            "title": "Document 1",
            "type": "Document",
            "path": "/site/doc1",
            "parent_path": "/site",
            "deletion_date": now - timedelta(days=1),
            "size": 1024,
            "object": Mock(),
        }

        self.storage["item2"] = {
            "id": "doc2",
            "title": "Document 2",
            "type": "Document",
            "path": "/site/doc2",
            "parent_path": "/site",
            "deletion_date": now,  # more recent
            "size": 2048,
            "object": Mock(),
        }

        # Get items
        items = self.recycle_bin.get_items()

        # Verify correct sorting (newest first) and data
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["recycle_id"], "item2")
        self.assertEqual(items[1]["recycle_id"], "item1")

        # Verify object is not included in listing
        self.assertNotIn("object", items[0])
        self.assertNotIn("object", items[1])

    @patch("Products.CMFPlone.recyclebin.IAnnotations")
    def test_get_item(self, IAnnotations_mock):
        """Test retrieving a specific item from the recycle bin"""
        # Configure mocks
        IAnnotations_mock.return_value = self.annotations_mock

        # Setup storage with test data
        self._setup_storage()
        test_obj = Mock()

        self.storage["test-id"] = {
            "id": "document",
            "object": test_obj,
            "title": "Test Document",
        }

        # Get existing item
        item = self.recycle_bin.get_item("test-id")
        self.assertEqual(item["id"], "document")
        self.assertEqual(item["object"], test_obj)

        # Get non-existent item
        item = self.recycle_bin.get_item("non-existent")
        self.assertIsNone(item)

    @patch("Products.CMFPlone.recyclebin.IAnnotations")
    def test_restore_item(self, IAnnotations_mock):
        """Test restoring an item from the recycle bin"""
        # Configure mocks
        IAnnotations_mock.return_value = self.annotations_mock

        # Setup storage with test data
        self._setup_storage()
        test_obj = Mock()

        # Setup target container mock
        target_container = Mock()
        target_container._setObject = Mock()
        target_container.__contains__ = lambda _, key: key in ["existing-doc"]
        target_container.__getitem__ = lambda _, key: (
            test_obj if key == "doc1" else None
        )

        # Test normal restoration
        self.storage["test-id"] = {
            "id": "doc1",
            "object": test_obj,
            "title": "Test Document",
            "parent_path": "/plone/folder",
        }

        # Mock site traversal
        self.site.unrestrictedTraverse.return_value = target_container

        # Restore item
        result = self.recycle_bin.restore_item("test-id")

        # Verify item was restored correctly
        target_container._setObject.assert_called_once_with("doc1", test_obj)
        self.assertEqual(result, test_obj)
        self.assertNotIn("test-id", self.storage)

        # Test ID conflict resolution
        self.storage["test-id2"] = {
            "id": "existing-doc",  # This ID already exists in the container
            "object": test_obj,
            "title": "Test Document",
            "parent_path": "/plone/folder",
        }

        # Need to reset the mock count for the second test
        target_container._setObject.reset_mock()

        # Restore with conflicting ID
        with patch("Products.CMFPlone.recyclebin.datetime") as dt_mock:
            dt_mock.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
            dt_mock.strftime = datetime.strftime

            self.recycle_bin.restore_item("test-id2")

            # Should have generated a new ID
            target_container._setObject.assert_called_once()
            call_args = target_container._setObject.call_args[0]
            self.assertTrue(call_args[0].startswith("existing-doc-restored-"))

        # Test non-existent item
        result = self.recycle_bin.restore_item("non-existent")
        self.assertIsNone(result)

    @patch("Products.CMFPlone.recyclebin.IAnnotations")
    def test_purge_item(self, IAnnotations_mock):
        """Test purging an item from the recycle bin"""
        # Configure mocks
        IAnnotations_mock.return_value = self.annotations_mock

        # Setup storage with test data
        self._setup_storage()

        # Add test item
        self.storage["test-id"] = {"id": "doc1"}

        # Purge existing item
        result = self.recycle_bin.purge_item("test-id")
        self.assertTrue(result)
        self.assertNotIn("test-id", self.storage)

        # Purge non-existent item
        result = self.recycle_bin.purge_item("non-existent")
        self.assertFalse(result)

    @patch("Products.CMFPlone.recyclebin.IAnnotations")
    @patch("Products.CMFPlone.recyclebin.getUtility")
    @patch("Products.CMFPlone.recyclebin.datetime")
    def test_purge_expired_items(
        self, datetime_mock, getUtility_mock, IAnnotations_mock
    ):
        """Test purging expired items from the recycle bin"""
        # Configure mocks
        now = datetime(2023, 1, 31)
        datetime_mock.now.return_value = now
        getUtility_mock.return_value = self.registry_mock
        IAnnotations_mock.return_value = self.annotations_mock

        # Setup storage with test data
        self._setup_storage()

        # Add items with different ages
        self.storage["recent"] = {
            "id": "recent-doc",
            "deletion_date": now - timedelta(days=10),  # Within retention period
        }

        self.storage["old1"] = {
            "id": "old-doc1",
            "deletion_date": now - timedelta(days=35),  # Expired
        }

        self.storage["old2"] = {
            "id": "old-doc2",
            "deletion_date": now - timedelta(days=40),  # Expired
        }

        # Test purging with auto_purge enabled
        count = self.recycle_bin.purge_expired_items()

        # Should have purged 2 items
        self.assertEqual(count, 2)
        self.assertIn("recent", self.storage)  # Should still be there
        self.assertNotIn("old1", self.storage)  # Should be purged
        self.assertNotIn("old2", self.storage)  # Should be purged

        # Test with auto_purge disabled
        self.settings_mock.auto_purge = False

        # Reset storage
        self._setup_storage()
        self.storage["old"] = {
            "id": "old-doc",
            "deletion_date": now - timedelta(days=100),  # Very old
        }

        count = self.recycle_bin.purge_expired_items()
        self.assertEqual(count, 0)  # Should not have purged anything
        self.assertIn("old", self.storage)  # Should still be there

    @patch("Products.CMFPlone.recyclebin.IAnnotations")
    @patch("Products.CMFPlone.recyclebin.getUtility")
    @patch("Products.CMFPlone.recyclebin.logger")
    def test_check_size_limits(self, logger_mock, getUtility_mock, IAnnotations_mock):
        """Test checking size limits and purging oldest items if needed"""
        # Configure mocks
        getUtility_mock.return_value = self.registry_mock
        IAnnotations_mock.return_value = self.annotations_mock

        # Set maximum size to 10 MB
        self.settings_mock.maximum_size = 10

        # Setup storage with test data
        self._setup_storage()

        # Add items of different sizes and dates
        # Total: 12 MB (exceeds the 10 MB limit)
        now = datetime.now()

        self.storage["item1"] = {
            "id": "doc1",
            "deletion_date": now - timedelta(days=10),
            "size": 5 * 1024 * 1024,  # 5 MB
        }

        self.storage["item2"] = {
            "id": "doc2",
            "deletion_date": now - timedelta(days=5),
            "size": 4 * 1024 * 1024,  # 4 MB
        }

        self.storage["item3"] = {
            "id": "doc3",
            "deletion_date": now,
            "size": 3 * 1024 * 1024,  # 3 MB
        }

        # Check size limits
        self.recycle_bin._check_size_limits()

        # The oldest item (item1) should be purged
        self.assertNotIn("item1", self.storage)
        self.assertIn("item2", self.storage)
        self.assertIn("item3", self.storage)
        self.assertEqual(len(logger_mock.info.mock_calls), 1)  # Should log the purge

    @patch("Products.CMFPlone.recyclebin.IAnnotations")
    @patch("Products.CMFPlone.recyclebin.getSite")
    def test_get_context(self, getSite_mock, IAnnotations_mock):
        """Test getting context when used as a utility"""
        # Create a recycle bin without context
        rb = RecycleBin()

        # Mock the site
        site_mock = Mock()
        getSite_mock.return_value = site_mock

        # Get context
        context = rb._get_context()

        # Should have called getSite
        getSite_mock.assert_called_once()
        self.assertEqual(context, site_mock)
