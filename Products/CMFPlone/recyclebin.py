from BTrees.OOBTree import OOBTree
from BTrees.OOBTree import OOTreeSet
from AccessControl import getSecurityManager
from datetime import datetime
from datetime import timedelta
from DateTime import DateTime
from persistent import Persistent
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.controlpanel.browser.recyclebin import (
    IRecycleBinControlPanelSettings,
)
from Products.CMFPlone.interfaces.recyclebin import IRecycleBin
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import implementer

import logging
import uuid


logger = logging.getLogger("Products.CMFPlone.RecycleBin")

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
            IRecycleBinControlPanelSettings, prefix="plone-recyclebin"
        )

    def is_enabled(self):
        """Check if recycle bin is enabled"""
        try:
            settings = self._get_settings()
            return settings.recycling_enabled
        except (KeyError, AttributeError):
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
        elif item_type == "CommentTree":
            # For comment trees, generate a title including the number of comments
            comment_count = len(obj.get("comments", []))
            root_comment = None

            # Try to find the root comment to get its text
            for comment, _ in obj.get("comments", []):
                if getattr(comment, "comment_id", None) == obj.get("root_comment_id"):
                    root_comment = comment
                    break

            # If we found the root comment, get a preview of its text
            comment_preview = ""
            if root_comment and hasattr(root_comment, "text"):
                # Take the first 30 characters of the text as a preview
                text = getattr(root_comment, "text", "")
                if text:
                    if len(text) > 30:
                        comment_preview = text[:30] + "..."
                    else:
                        comment_preview = text

            # Create a meaningful title
            if comment_preview:
                return f'Comment thread: "{comment_preview}" ({comment_count} comments)'
            else:
                return f"Comment thread ({comment_count} comments)"
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
            # Store basic data for this child
            child_data = {
                "id": child_id,
                "title": self._get_item_title(child),
                "type": getattr(child, "portal_type", "Unknown"),
                "path": child_path,
                "parent_path": folder_path,
                "deletion_date": datetime.now(),
                "size": getattr(child, "get_size", lambda: 0)(),
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

    def add_item(self, obj, original_container, original_path, item_type=None):
        """Add deleted item to recycle bin"""
        if not self.is_enabled():
            return None

        # Get the original id but if not found then generate a unique ID for the recycled item
        item_id = obj.getId() if hasattr(obj, "getId") else getattr(obj, "id", str(uuid.uuid4()))

        # Add a workflow history entry about the deletion if possible
        self._update_workflow_history(obj, 'deletion')

        # Generate a meaningful title
        item_title = self._get_item_title(obj, item_type)

        # Handle folders and collections specially
        children = {}
        if hasattr(obj, "objectIds") or item_type == "Collection":
            if hasattr(obj, "objectIds"):
                # Process all children recursively
                children = self._process_folder_children(obj, original_path)

        # Store metadata about the deletion
        parent_path = (
            "/".join(original_container.getPhysicalPath())
            if original_container
            else "/".join(original_path.split("/")[:-1])
        )

        storage_data = {
            "id": item_id,
            "title": item_title,
            "type": item_type or getattr(obj, "portal_type", "Unknown"),
            "path": original_path,
            "parent_path": parent_path,
            "deletion_date": datetime.now(),
            "size": getattr(obj, "get_size", lambda: 0)(),
            "object": obj,  # Store the actual object
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
        if not hasattr(obj, 'workflow_history'):
            return
            
        workflow_tool = getToolByName(self._get_context(), 'portal_workflow')
        chains = workflow_tool.getChainFor(obj)
        
        if not chains:
            return
            
        workflow_id = chains[0]
        history = obj.workflow_history.get(workflow_id, ())
        
        if not history:
            return
            
        history = list(history)
        current_state = history[-1].get('review_state', None) if history else None
        user_id = getSecurityManager().getUser().getId() or 'System'
        
        entry = {
            'action': 'Moved to recycle bin' if action_type == 'deletion' else 'Restored from recycle bin',
            'actor': user_id,
            'comments': 'Item was deleted and moved to recycle bin' if action_type == 'deletion' else 'Restored from recycle bin after deletion',
            'time': DateTime(),
            'review_state': current_state,
        }
            
        # Add the entry and update the history
        history.append(entry)
        obj.workflow_history[workflow_id] = tuple(history)

    def _find_target_container(self, target_container, parent_path):
        """Helper to find the target container for restoration"""
        site = self._get_context()
        if target_container is None:
            # Try to get the original parent
            try:
                target_container = site.unrestrictedTraverse(parent_path)
            except (KeyError, AttributeError):
                # We need an explicit target container if original parent is gone
                raise ValueError(
                    f"Original parent container at {parent_path} no longer exists. "
                    "You must specify a target_container to restore this item."
                )
        return target_container

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
        item_type = item_data.get("type", None)

        # Special handling for CommentTree (comments with replies)
        if item_type == "CommentTree":
            return self._restore_comment_tree(item_id, item_data, target_container)

        # Special handling for Discussion Item (Comments)
        if item_data.get("type") == "Discussion Item":
            return self._restore_comment(item_id, item_data, target_container)

        # Regular content object restoration
        # Find the container to restore to
        target_container = self._find_target_container(target_container, item_data["parent_path"])
        
        # Make sure we don't overwrite existing content
        self._handle_existing_object(obj_id, target_container, obj)

        # Set the new ID if it was changed
        if obj_id != item_data["id"]:
            obj.id = obj_id

        # Add object to the target container
        target_container[obj_id] = obj

        # Add a workflow history entry about the restoration
        restored_obj = target_container[obj_id]
        self._update_workflow_history(restored_obj, 'restoration', item_data)

        # Remove from recycle bin
        del self.storage[item_id]

        # Clean up any child items 
        self._cleanup_child_references(item_data)

        return restored_obj

    def _find_parent_comment(self, comment, original_in_reply_to, conversation, id_mapping=None):
        """Helper method to find parent comment during restoration"""
        id_mapping = id_mapping or {}
        if original_in_reply_to is None or original_in_reply_to == 0:
            return False, None
        
        # First check if parent exists directly (not previously deleted)
        if original_in_reply_to in conversation:
            return True, original_in_reply_to
            
        # Then check if it was restored with a different ID using mapping
        if str(original_in_reply_to) in id_mapping:
            # Use the ID mapping to find the new ID
            new_parent_id = id_mapping[str(original_in_reply_to)]
            return True, new_parent_id
            
        # Look through all comments for original_id matching our in_reply_to
        for comment_id in conversation.keys():
            comment_obj = conversation[comment_id]
            comment_original_id = getattr(comment_obj, "original_id", None)
            if comment_original_id is not None and str(comment_original_id) == str(original_in_reply_to):
                # Found the parent with a new ID
                return True, comment_id

        # No parent found
        return False, None

    def _restore_comment(self, item_id, item_data, target_container=None):
        """Enhanced restoration method for comments that preserves reply relationships"""
        obj = item_data["object"]
        site = self._get_context()

        # Try to find the original conversation
        parent_path = item_data["parent_path"]
        try:
            conversation = site.unrestrictedTraverse(parent_path)
        except (KeyError, AttributeError):
            logger.warning(
                f"Cannot restore comment {item_id}: conversation no longer exists at {parent_path}"
            )
            return None

        # Restore comment back to conversation
        from plone.app.discussion.interfaces import IConversation

        if not IConversation.providedBy(conversation):
            logger.warning(
                f"Cannot restore comment {item_id}: parent is not a conversation"
            )
            return None

        # Store the original comment ID before restoration
        original_id = getattr(obj, "comment_id", None)
        original_in_reply_to = getattr(obj, "in_reply_to", None)

        # Track comment relationships using a request-based dictionary
        from zope.globalrequest import getRequest

        request = getRequest()
        if request and not hasattr(request, "_comment_restore_mapping"):
            request._comment_restore_mapping = {}

        # Initialize mapping if needed
        mapping = getattr(request, "_comment_restore_mapping", {})
        conversation_path = "/".join(conversation.getPhysicalPath())
        if conversation_path not in mapping:
            mapping[conversation_path] = {}

        id_mapping = mapping[conversation_path]

        # Check if the parent comment exists in the conversation
        parent_found, new_parent_id = self._find_parent_comment(
            obj, original_in_reply_to, conversation, id_mapping
        )

        # Update the in_reply_to reference or make it a top-level comment
        if parent_found:
            obj.in_reply_to = new_parent_id
        else:
            # If no parent was found, make this a top-level comment
            obj.in_reply_to = None

        # Store the original ID for future reference
        if not hasattr(obj, "original_id"):
            obj.original_id = original_id

        # Add the comment to the conversation
        new_id = conversation.addComment(obj)

        # Store the mapping of original ID to new ID
        if original_id is not None:
            id_mapping[str(original_id)] = new_id

        # Remove from recycle bin
        del self.storage[item_id]

        # Return the restored comment
        return conversation[new_id]

    def _restore_comment_tree(self, item_id, item_data, target_container=None):
        """Restore a comment tree with all its replies while preserving relationships"""
        comment_tree = item_data["object"]
        root_comment_id = comment_tree.get("root_comment_id")
        comments_to_restore = comment_tree.get("comments", [])

        logger.info(
            f"Attempting to restore comment tree {item_id} with root_comment_id: {root_comment_id}"
        )
        logger.info(f"Found {len(comments_to_restore)} comments to restore")

        if not comments_to_restore:
            logger.warning(
                f"Cannot restore comment tree {item_id}: no comments found in tree"
            )
            return None

        site = self._get_context()

        # Try to find the original conversation
        parent_path = item_data["parent_path"]
        try:
            conversation = site.unrestrictedTraverse(parent_path)
        except (KeyError, AttributeError):
            logger.warning(
                f"Cannot restore comment tree {item_id}: conversation no longer exists at {parent_path}"
            )
            return None

        # Restore comments back to conversation
        from plone.app.discussion.interfaces import IConversation

        if not IConversation.providedBy(conversation):
            logger.warning(
                f"Cannot restore comment tree {item_id}: parent is not a conversation"
            )
            return None

        # First extract all comments and create a mapping of original IDs
        # to comment objects for quick lookup
        comment_dict = {}
        id_mapping = {}  # Will map original IDs to new IDs

        # Process comments to build reference dictionary
        for comment_obj, _ in comments_to_restore:
            # Store original values we'll need for restoration
            original_id = getattr(comment_obj, "comment_id", None)
            original_in_reply_to = getattr(comment_obj, "in_reply_to", None)

            logger.info(
                f"Processing comment with ID: {original_id}, in_reply_to: {original_in_reply_to}"
            )

            # Mark with original ID for future reference
            if not hasattr(comment_obj, "original_id"):
                comment_obj.original_id = original_id

            # Store in dictionary for quick access
            comment_dict[original_id] = {
                "comment": comment_obj,
                "in_reply_to": original_in_reply_to,
            }

        # Find the root comment
        root_comment = None
        if root_comment_id in comment_dict:
            root_comment = comment_dict[root_comment_id]["comment"]
        else:
            # Try to find a top-level comment to use as root
            for comment_id, comment_data in comment_dict.items():
                in_reply_to = comment_data["in_reply_to"]
                if in_reply_to == 0 or in_reply_to is None:
                    # Found a top-level comment, use as root
                    root_comment = comment_data["comment"]
                    root_comment_id = comment_id
                    break

            # If still no root, use the first comment
            if not root_comment and comment_dict:
                first_key = list(comment_dict.keys())[0]
                root_comment = comment_dict[first_key]["comment"]
                root_comment_id = first_key

        if not root_comment:
            logger.error(
                f"Cannot restore comment tree {item_id}: no valid root comment could be determined"
            )
            return None

        # Check if the parent comment exists
        original_in_reply_to = getattr(root_comment, "in_reply_to", None)
        parent_found, new_parent_id = self._find_parent_comment(
            root_comment, original_in_reply_to, conversation
        )
        
        if parent_found:
            root_comment.in_reply_to = new_parent_id
        else:
            root_comment.in_reply_to = None

        # Add the root comment to the conversation
        new_root_id = conversation.addComment(root_comment)
        id_mapping[root_comment_id] = new_root_id

        # Now restore all child comments, skipping the root comment
        remaining_comments = {
            k: v for k, v in comment_dict.items() if k != root_comment_id
        }

        # Track successfully restored comments
        restored_count = 1  # Start with 1 for root

        # Keep trying to restore comments until no more can be restored
        max_passes = 10  # Limit passes to avoid infinite loops
        current_pass = 0

        while remaining_comments and current_pass < max_passes:
            current_pass += 1
            restored_in_pass = 0

            # Copy keys to avoid modifying dict during iteration
            comment_ids = list(remaining_comments.keys())

            for comment_id in comment_ids:
                comment_data = remaining_comments[comment_id]
                comment_obj = comment_data["comment"]
                original_in_reply_to = comment_data["in_reply_to"]

                # Try to find the parent in our mapping
                parent_found = False
                new_parent_id = None

                # If original parent was the root comment
                if str(original_in_reply_to) == str(root_comment_id):
                    parent_found = True
                    new_parent_id = new_root_id
                # Or if it was another already restored comment
                elif str(original_in_reply_to) in id_mapping:
                    parent_found = True
                    new_parent_id = id_mapping[str(original_in_reply_to)]
                # Or try to find it directly in the conversation
                else:
                    parent_found, new_parent_id = self._find_parent_comment(
                        comment_obj, original_in_reply_to, conversation, id_mapping
                    )

                if parent_found:
                    # We found the parent, update reference and restore
                    comment_obj.in_reply_to = new_parent_id
                    
                    # Store original ID for future reference
                    if not hasattr(comment_obj, "original_id"):
                        comment_obj.original_id = comment_id

                    # Add to conversation
                    try:
                        new_id = conversation.addComment(comment_obj)
                        id_mapping[comment_id] = new_id
                        del remaining_comments[comment_id]
                        restored_in_pass += 1
                    except Exception as e:
                        logger.error(f"Error restoring comment {comment_id}: {e}")

            # If we didn't restore any comments in this pass and still have comments left,
            # something is wrong with the parent references
            if restored_in_pass == 0 and remaining_comments:
                # Make any remaining comments top-level comments
                for comment_id, comment_data in list(remaining_comments.items()):
                    try:
                        comment_obj = comment_data["comment"]
                        comment_obj.in_reply_to = None  # Make it a top-level comment
                        
                        # Store original ID for future reference
                        if not hasattr(comment_obj, "original_id"):
                            comment_obj.original_id = comment_id
                        
                        new_id = conversation.addComment(comment_obj)
                        id_mapping[comment_id] = new_id
                        del remaining_comments[comment_id]
                        restored_in_pass += 1
                    except Exception as e:
                        logger.error(f"Error forcing comment {comment_id} as top-level: {e}")
                
                # Break out of the loop since we've tried our best
                break

            restored_count += restored_in_pass
            
            # If all comments were restored, exit the loop
            if not remaining_comments:
                break

        # Clean up and return
        del self.storage[item_id]
        logger.info(f"Restored {restored_count} comments from comment tree {item_id}")
        
        # Return the root comment as the result
        return conversation.get(new_root_id) if new_root_id in conversation else None

    def purge_item(self, item_id):
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
            if "children" in item_data and isinstance(item_data["children"], dict):
                def purge_children(children_dict):
                    for child_id, child_data in list(children_dict.items()):
                        # If this child has children, recursively purge them first
                        if "children" in child_data and isinstance(child_data["children"], dict):
                            purge_children(child_data["children"])
                # Start the recursive purge of children
                purge_children(item_data["children"])
                
            # Simply remove from storage - the object will be garbage collected
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
            
            # Use the sorted index for efficient date-based queries
            # Iterate through items from oldest to newest
            for item_id, data in list(self.storage.get_items_sorted_by_date(reverse=False)):
                deletion_date = data.get("deletion_date")
                if deletion_date and deletion_date < cutoff_date:
                    if self.purge_item(item_id):
                        purge_count += 1
                        logger.info(f"Item {item_id} purged due to retention policy (deleted on {deletion_date})")
                else:
                    # Since items are sorted by date, once we find one that's 
                    # newer than the cutoff date, we can stop checking
                    break
                    
            return purge_count
        except Exception as e:
            logger.error(f"Error purging expired items: {str(e)}")
            return 0

    def _check_size_limits(self):
        """Check if the recycle bin exceeds size limits and purge oldest items if needed"""
        try:
            settings = self._get_settings()
            max_size_bytes = settings.maximum_size * 1024 * 1024  # Convert MB to bytes
            
            # If max_size is 0, size limiting is disabled
            if max_size_bytes <= 0:
                return
                
            total_size = 0
            items_by_date = []
            
            # Calculate total size using items sorted by date (oldest first)
            for item_id, data in self.storage.get_items_sorted_by_date(reverse=False):
                size = data.get("size", 0)
                total_size += size
                items_by_date.append((item_id, size))
                
            # If we're under the limit, nothing to do
            if total_size <= max_size_bytes:
                return
                
            logger.info(f"Recycle bin size ({total_size / (1024 * 1024):.2f} MB) exceeds limit ({max_size_bytes / (1024 * 1024):.2f} MB)")
            
            # Remove oldest items if size limit is exceeded
            for item_id, size in items_by_date:
                if total_size <= max_size_bytes:
                    break
                    
                if self.purge_item(item_id):
                    total_size -= size
                    logger.info(f"Purged item {item_id} due to size constraints")
        except Exception as e:
            logger.error(f"Error checking size limits: {str(e)}")
