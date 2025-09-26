from AccessControl import getSecurityManager
from Acquisition import aq_base
from BTrees.OOBTree import OOBTree
from BTrees.OOBTree import OOTreeSet
from datetime import datetime
from datetime import timedelta
from DateTime import DateTime
from persistent import Persistent
from plone.base.interfaces.recyclebin import IRecycleBin
from plone.base.interfaces.recyclebin import IRecycleBinControlPanelSettings
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import implementer

import logging
import uuid


logger = logging.getLogger(__name__)

ANNOTATION_KEY = "Products.CMFPlone.RecycleBin"


class RecycleBinStorage(Persistent):
    """Storage class for RecycleBin using BTrees for better performance"""

    def __init__(self):
        self.items = OOBTree()
        # Add a sorted index that stores (deletion_date, item_id) tuples
        # This will automatically maintain items sorted by date
        self._sorted_index = OOTreeSet()

    def __getitem__(self, key):
        return self.items[key]

    def __setitem__(self, key, value):
        # When adding or updating an item, update the sorted index
        if key in self.items:
            # If updating an existing item, remove old index entry first
            old_value = self.items[key]
            self._remove_from_index(key, old_value)

        # Add the item to main storage
        self.items[key] = value

        # Add to sorted index if it has a deletion_date
        self._add_to_index(key, value)

    def __delitem__(self, key):
        # When deleting an item, also remove it from the sorted index
        if key in self.items:
            item = self.items[key]
            self._remove_from_index(key, item)

        # Remove from main storage
        del self.items[key]

    def _add_to_index(self, key, value):
        """Add an item to the sorted index"""
        if "deletion_date" in value:
            try:
                # Store as (date, id) for automatic sorting
                self._sorted_index.add((value["deletion_date"], key))
            except TypeError:
                # Skip if the date is not comparable
                logger.warning(
                    f"Could not index item {key} by date: {value.get('deletion_date')}"
                )

    def _remove_from_index(self, key, value):
        """Remove an item from the sorted index"""
        if "deletion_date" in value:
            try:
                sort_key = (value["deletion_date"], key)
                if sort_key in self._sorted_index:
                    self._sorted_index.remove(sort_key)
            except (KeyError, TypeError):
                # Ignore errors if the entry doesn't exist or date is not comparable
                pass

    def __contains__(self, key):
        return key in self.items

    def __len__(self):
        return len(self.items)

    def get(self, key, default=None):
        return self.items.get(key, default)

    def keys(self):
        return self.items.keys()

    def values(self):
        return self.items.values()

    def get_items(self):
        """Return all items as key-value pairs"""
        return self.items.items()

    def get_items_sorted_by_date(self, reverse=True):
        """Return items sorted by deletion date

        Args:
            reverse: If True, return newest items first (default),
                    if False, return oldest items first

        Returns:
            Generator yielding (item_id, item_data) tuples
        """
        sorted_keys = list(self._sorted_index)

        # If we want newest first (reverse=True), reverse the list
        if reverse:
            sorted_keys.reverse()

        # Yield items in the requested order
        for date, item_id in sorted_keys:
            if item_id in self.items:  # Double check item still exists
                yield (item_id, self.items[item_id])


@implementer(IRecycleBin)
class RecycleBin:
    """Stores deleted content items"""

    def __init__(self):
        """Initialize the recycle bin utility

        It will get the context (Plone site) on demand using getSite()
        """
        pass

    def _get_context(self):
        """Get the context (Plone site)"""
        return getSite()

    def _get_storage(self):
        """Get the storage for recycled items"""
        context = self._get_context()
        annotations = IAnnotations(context)

        if ANNOTATION_KEY not in annotations:
            annotations[ANNOTATION_KEY] = RecycleBinStorage()

        return annotations[ANNOTATION_KEY]

    # Update property for storage to use _get_storage
    @property
    def storage(self):
        return self._get_storage()

    def _get_settings(self):
        """Get recycle bin settings from registry"""
        registry = getUtility(IRegistry)
        return registry.forInterface(
            IRecycleBinControlPanelSettings, prefix="recyclebin-controlpanel"
        )

    def is_enabled(self):
        """Check if recycle bin is enabled"""
        try:
            settings = self._get_settings()
            return settings.recycling_enabled
        except Exception as e:
            logger.error(
                f"Error checking recycle bin settings: {str(e)}. Recycling is disabled."
            )
            return False

    def _get_item_title(self, obj, item_type=None):
        """Helper method to get a meaningful title for an item"""
        if hasattr(obj, "objectIds") or item_type == "Collection":
            # For folders and collections
            return (
                obj.Title()
                if hasattr(obj, "Title")
                else getattr(obj, "title", "Unknown")
            )

        else:
            # For regular items, use Title() if available
            return (
                obj.Title()
                if hasattr(obj, "Title")
                else getattr(obj, "title", "Unknown")
            )

    def _process_folder_children(self, folder_obj, folder_path):
        """Helper method to process folder children recursively"""
        folder_children = {}
        for child_id in folder_obj.objectIds():
            child = folder_obj[child_id]
            child_path = f"{folder_path}/{child_id}"
            # Get workflow state for this child
            child_workflow_state = None
            workflow_tool = getToolByName(self._get_context(), "portal_workflow")
            child_workflow_state = workflow_tool.getInfoFor(child, "review_state", None)

            # Store basic data for this child
            child_data = {
                "id": child_id,
                "title": self._get_item_title(child),
                "type": getattr(child, "portal_type", "Unknown"),
                "path": child_path,
                "parent_path": folder_path,
                "deletion_date": datetime.now(),
                "size": getattr(child, "get_size", lambda: 0)(),
                "language": getattr(child, "language", None)
                or getattr(child, "Language", lambda: None)(),
                "workflow_state": child_workflow_state,
                "object": child,
            }

            # If this child is also a folder, process its children
            if hasattr(child, "objectIds") and child.objectIds():
                nested_children = self._process_folder_children(child, child_path)
                if nested_children:
                    child_data["children"] = nested_children
                    child_data["children_count"] = len(nested_children)

            folder_children[child_id] = child_data
        return folder_children

    def add_item(
        self,
        obj,
        original_container,
        original_path,
        item_type=None,
        process_children=True,
    ):
        """Add deleted item to recycle bin"""
        if not self.is_enabled():
            return None

        # Get the original id but if not found then generate a unique ID for the recycled item
        item_id = (
            obj.getId()
            if hasattr(obj, "getId")
            else getattr(obj, "id", str(uuid.uuid4()))
        )

        # Add a workflow history entry about the deletion if possible
        self._update_workflow_history(obj, "deletion")

        # Generate a meaningful title
        item_title = self._get_item_title(obj, item_type)

        # Handle folders and collections specially
        children = {}
        if process_children and (
            hasattr(obj, "objectIds") or item_type == "Collection"
        ):
            if hasattr(obj, "objectIds"):
                # Process all children recursively
                children = self._process_folder_children(obj, original_path)

        # Store metadata about the deletion
        parent_path = (
            "/".join(original_container.getPhysicalPath())
            if original_container
            else "/".join(original_path.split("/")[:-1])
        )

        # Get the current user who is deleting the item
        user_id = getSecurityManager().getUser().getId() or "System"

        # Get workflow state at time of deletion
        workflow_state = None
        workflow_tool = getToolByName(self._get_context(), "portal_workflow")
        workflow_state = workflow_tool.getInfoFor(obj, "review_state", None)

        storage_data = {
            "id": item_id,
            "title": item_title,
            "type": item_type or getattr(obj, "portal_type", "Unknown"),
            "path": original_path,
            "parent_path": parent_path,
            "deletion_date": datetime.now(),
            "deleted_by": user_id,
            "size": getattr(obj, "get_size", lambda: 0)(),
            "language": getattr(obj, "language", None)
            or getattr(obj, "Language", lambda: None)(),
            "workflow_state": workflow_state,
            "object": aq_base(obj),  # Store the actual object with no acquisition chain
        }

        # Add children data if this was a folder/collection
        if children:
            storage_data["children"] = children
            storage_data["children_count"] = len(children)

        # Generate a unique recycle ID
        recycle_id = str(uuid.uuid4())
        self.storage[recycle_id] = storage_data

        # Check if we need to clean up old items
        self._check_size_limits()
        self._purge_expired_items()

        return recycle_id

    def get_items(self):
        """Return all items in recycle bin"""
        items = []
        # Use the pre-sorted index to get items by date (newest first)
        for item_id, data in self.storage.get_items_sorted_by_date(reverse=True):
            # Only copy the essential metadata instead of the entire data dictionary
            item_data = {
                "recycle_id": item_id,
                "id": data.get("id", ""),
                "title": data.get("title", ""),
                "type": data.get("type", "Unknown"),
                "path": data.get("path", ""),
                "parent_path": data.get("parent_path", ""),
                "deletion_date": data.get("deletion_date"),
                "deleted_by": data.get("deleted_by", "Unknown"),
                "size": data.get("size", 0),
            }

            # Copy any other metadata but not the actual object
            for key, value in data.items():
                if key != "object" and key not in item_data:
                    item_data[key] = value

            items.append(item_data)

        return items

    def get_item(self, item_id):
        """Get a specific deleted item by ID"""
        return self.storage.get(item_id)

    def _update_workflow_history(self, obj, action_type, item_data=None):
        """Add a workflow history entry about deletion or restoration

        Args:
            obj: The content object
            action_type: Either 'deletion' or 'restoration'
            item_data: The recyclebin storage data (needed for restoration to show deletion date)
        """
        if not hasattr(obj, "workflow_history"):
            return

        workflow_tool = getToolByName(self._get_context(), "portal_workflow")
        chains = workflow_tool.getChainFor(obj)

        if not chains:
            return

        workflow_id = chains[0]
        history = obj.workflow_history.get(workflow_id, ())

        if not history:
            return

        history = list(history)
        current_state = history[-1].get("review_state", None) if history else None
        user_id = getSecurityManager().getUser().getId() or "System"

        entry = {
            "action": (
                "Moved to recycle bin"
                if action_type == "deletion"
                else "Restored from recycle bin"
            ),
            "actor": user_id,
            "comments": (
                "Item was deleted and moved to recycle bin"
                if action_type == "deletion"
                else "Restored from recycle bin after deletion"
            ),
            "time": DateTime(),
            "review_state": current_state,
        }

        # Add the entry and update the history
        history.append(entry)
        obj.workflow_history[workflow_id] = tuple(history)

    def _reset_workflow_state_if_needed(self, obj):
        """Reset object workflow state to initial state if the setting is enabled"""
        settings = self._get_settings()
        if not settings.restore_to_initial_state:
            return

        workflow_tool = getToolByName(self._get_context(), "portal_workflow")
        chains = workflow_tool.getChainFor(obj)

        if not chains:
            return

        workflow_id = chains[0]
        workflow = workflow_tool.getWorkflowById(workflow_id)

        if not workflow:
            return

        # Get the initial state of the workflow
        initial_state = getattr(workflow, "initial_state", None)
        if not initial_state:
            logger.warning(
                f"Could not determine initial state for workflow {workflow_id}"
            )
            return

        # Get current state
        current_state = workflow_tool.getInfoFor(obj, "review_state", None)

        # Only reset if current state is different from initial state
        if current_state != initial_state:
            # Reset the workflow state by updating the workflow history
            if hasattr(obj, "workflow_history") and workflow_id in obj.workflow_history:
                history = list(obj.workflow_history[workflow_id])
                if history:
                    # Update the last entry to reflect the state reset
                    user_id = getSecurityManager().getUser().getId() or "System"

                    reset_entry = {
                        "action": "Reset to initial state",
                        "actor": user_id,
                        "comments": f"Workflow state reset to '{initial_state}' during restoration from recycle bin",
                        "time": DateTime(),
                        "review_state": initial_state,
                    }

                    history.append(reset_entry)
                    obj.workflow_history[workflow_id] = tuple(history)

                    # Force the object's state to be updated
                    workflow._changeStateOf(obj, workflow.states[initial_state])

                    logger.info(
                        f"Reset workflow state of {obj.getId()} from '{current_state}' to '{initial_state}'"
                    )

    def _reset_folder_children_workflow_if_needed(self, folder_obj):
        """Recursively reset workflow states of folder children if the setting is enabled"""
        settings = self._get_settings()
        if not settings.restore_to_initial_state:
            return

        # Check if this is a folder-like object
        if not hasattr(folder_obj, "objectIds"):
            return

        # Recursively reset workflow states for all children
        for child_id in folder_obj.objectIds():
            child = folder_obj[child_id]
            self._reset_workflow_state_if_needed(child)

            # If the child is also a folder, recurse
            if hasattr(child, "objectIds"):
                self._reset_folder_children_workflow_if_needed(child)

    def _find_target_container(self, target_container, parent_path):
        """Helper to find the target container for restoration

        Returns a tuple (success, container, error_message) where:
            - success: Boolean indicating if the container was found
            - container: The container object (None if not found)
            - error_message: Error message if success is False
        """
        site = self._get_context()
        if target_container is None:
            # Try to get the original parent
            try:
                target_container = site.unrestrictedTraverse(parent_path)
                return True, target_container, None
            except (KeyError, AttributeError):
                # We need an explicit target container if original parent is gone
                error_message = (
                    f"Original parent container at {parent_path} no longer exists. "
                    "You must specify a target_container to restore this item."
                )
                return False, None, error_message
        return True, target_container, None

    def _cleanup_child_references(self, item_data):
        """Clean up any child items associated with a parent that was restored"""
        if "children" in item_data and isinstance(item_data["children"], dict):
            logger.info(
                f"Cleaning up {len(item_data['children'])} child items from recyclebin"
            )

            # Define a function to recursively process nested folders
            def cleanup_children(children_dict):
                for child_id, child_data in children_dict.items():
                    # Clean up any entries that might match this child
                    child_path = child_data.get("path")
                    child_orig_id = child_data.get("id")

                    for storage_id, storage_data in list(self.storage.get_items()):
                        if (
                            storage_data.get("path") == child_path
                            or storage_data.get("id") == child_orig_id
                        ):
                            logger.info(
                                f"Removing child item {child_orig_id} from recyclebin"
                            )
                            if storage_id in self.storage:
                                del self.storage[storage_id]

                    # If this child is also a folder, recursively process its children
                    if "children" in child_data and isinstance(
                        child_data["children"], dict
                    ):
                        cleanup_children(child_data["children"])

            # Start the recursive cleanup
            cleanup_children(item_data["children"])

    def _handle_existing_object(self, obj_id, target_container, obj):
        """Handle cases where an object with the same ID already exists in target"""
        if obj_id in target_container:
            # Check if explicit restoration is requested
            if getattr(obj, "_v_restoring_from_recyclebin", False):
                # We were explicitly asked to restore this item, so delete existing item first
                logger.info(
                    f"Removing existing object {obj_id} to restore recycled version"
                )
                target_container._delObject(obj_id)
            else:
                # Raise a meaningful exception instead of generating a new ID
                raise ValueError(
                    f"Cannot restore item '{obj_id}' because an item with this ID already exists in the target location. "
                    f"To replace the existing item with the recycled one, use the recycle bin interface."
                )

    def restore_item(self, item_id, target_container=None):
        """Restore item to original location or specified container"""
        if item_id not in self.storage:
            return None

        item_data = self.storage[item_id]
        obj = item_data["object"]
        obj_id = item_data["id"]

        # Regular content object restoration
        # Find the container to restore to
        success, target_container, error_message = self._find_target_container(
            target_container, item_data["parent_path"]
        )

        # If we couldn't find the target container, return the error message
        if not success:
            return {"success": False, "error": error_message}

        # Make sure we don't overwrite existing content
        self._handle_existing_object(obj_id, target_container, obj)

        # Set the new ID if it was changed
        if obj_id != item_data["id"]:
            obj.id = obj_id

        # Add object to the target container
        target_container[obj_id] = obj

        # Add a workflow history entry about the restoration
        restored_obj = target_container[obj_id]
        self._update_workflow_history(restored_obj, "restoration", item_data)

        # Reset workflow state to initial state if the setting is enabled
        self._reset_workflow_state_if_needed(restored_obj)

        # Also reset workflow states of children if this is a folder
        self._reset_folder_children_workflow_if_needed(restored_obj)

        restored_obj.reindexObject()

        # Remove from recycle bin
        del self.storage[item_id]

        # Clean up any child items
        self._cleanup_child_references(item_data)

        return restored_obj

    def purge_item(self, item_id) -> bool:
        """Permanently delete an item from the recycle bin

        Args:
            item_id: The ID of the item in the recycle bin

        Returns:
            Boolean indicating success
        """
        if item_id not in self.storage:
            logger.warning(f"Cannot purge item {item_id}: not found in recycle bin")
            return False

        try:
            # Purge any nested children first if this is a folder
            item_data = self.storage[item_id]
            item_path = item_data.get("path", "")

            if "children" in item_data and isinstance(item_data["children"], dict):
                # Find and purge standalone recycle bin entries for each child
                def purge_children(children_dict, parent_path):
                    for child_id, child_data in list(children_dict.items()):
                        child_path = f"{parent_path}/{child_id}"

                        # Find any standalone entries for this child in the recycle bin
                        for rec_id, rec_data in list(self.storage.get_items()):
                            if rec_id != item_id and rec_data.get("path") == child_path:
                                logger.info(
                                    f"Purging standalone entry for child: {child_path} (ID: {rec_id})"
                                )
                                del self.storage[rec_id]

                        # If this child has children, recursively purge them first
                        if "children" in child_data and isinstance(
                            child_data["children"], dict
                        ):
                            purge_children(child_data["children"], child_path)

                # Start the recursive purge of children
                purge_children(item_data["children"], item_path)

            # Remove the main item from storage - the object will be garbage collected
            del self.storage[item_id]
            logger.info(f"Item {item_id} purged from recycle bin")
            return True
        except Exception as e:
            logger.error(f"Error purging item {item_id}: {str(e)}")
            return False

    def _purge_expired_items(self):
        """Purge items that exceed the retention period

        Returns:
            Number of items purged
        """
        try:
            settings = self._get_settings()
            retention_days = settings.retention_period

            # If retention_period is 0, auto-purging is disabled
            if retention_days <= 0:
                logger.debug("Auto-purging is disabled (retention_period = 0)")
                return 0

            cutoff_date = datetime.now() - timedelta(days=retention_days)
            purge_count = 0

            # Use sorted index for efficient date-based removal (oldest first)
            for item_id, data in list(
                self.storage.get_items_sorted_by_date(reverse=False)
            ):
                deletion_date = data.get("deletion_date")

                # If item is older than retention period, purge it
                if deletion_date and deletion_date < cutoff_date:
                    if self.purge_item(item_id):
                        purge_count += 1
                        logger.info(
                            f"Item {item_id} purged due to retention policy (deleted on {deletion_date})"
                        )
                else:
                    # Since items are sorted by date, once we find an item newer than
                    # the cutoff date, we can stop checking
                    break

            return purge_count

        except Exception as e:
            logger.error(f"Error purging expired items: {str(e)}")
            return 0

    def _check_size_limits(self):
        """Check if the recycle bin exceeds size limits and purge oldest items if needed

        This method enforces the maximum size limit for the recycle bin by removing
        the oldest items when the limit is exceeded.
        """
        try:
            settings = self._get_settings()
            max_size_mb = settings.maximum_size

            # If max_size is 0, size limiting is disabled
            if max_size_mb <= 0:
                logger.debug("Size limiting is disabled (maximum_size = 0)")
                return

            max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
            total_size = 0
            items_by_date = []

            # Get items sorted by date (oldest first) and calculate total size
            for item_id, data in self.storage.get_items_sorted_by_date(reverse=False):
                size = data.get("size", 0)
                total_size += size
                items_by_date.append((item_id, size))

            # If we're under the limit, nothing to do
            if total_size <= max_size_bytes:
                return

            # Log the size excess
            logger.info(
                f"Recycle bin size ({total_size / (1024 * 1024):.2f} MB) exceeds limit ({max_size_mb} MB)"
            )

            # Remove oldest items until we're under the limit
            items_purged = 0
            for item_id, size in items_by_date:
                # Stop once we're under the limit
                if total_size <= max_size_bytes:
                    break

                if self.purge_item(item_id):
                    total_size -= size
                    items_purged += 1

            if items_purged:
                logger.info(
                    f"Purged {items_purged} oldest item{'s' if items_purged != 1 else ''} due to size constraints"
                )

        except Exception as e:
            logger.error(f"Error enforcing size limits: {str(e)}")
