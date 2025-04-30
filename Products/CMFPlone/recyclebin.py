from datetime import datetime
from datetime import timedelta
from persistent.mapping import PersistentMapping
from plone.registry.interfaces import IRegistry
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


@implementer(IRecycleBin)
class RecycleBin:
    """Stores deleted content items"""

    def __init__(self, context=None):
        """Initialize the recycle bin for a site

        Args:
            context: The Plone site object (optional when used as a utility)
        """
        self.context = context
        # When used as a utility without context, we'll get the context on demand

    def _get_context(self):
        """Get the context (Plone site) if not already available"""
        if self.context is None:
            self.context = getSite()
        return self.context

    def _get_storage(self):
        """Get the storage for recycled items"""
        context = self._get_context()
        annotations = IAnnotations(context)

        if ANNOTATION_KEY not in annotations:
            annotations[ANNOTATION_KEY] = PersistentMapping()

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

    def add_item(self, obj, original_container, original_path, item_type=None):
        """Add deleted item to recycle bin"""
        if not self.is_enabled():
            return None

        # Generate a unique ID for the recycled item
        item_id = str(uuid.uuid4())

        # Generate a meaningful title
        item_title = "Unknown"
        if item_type == "CommentTree":
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
                item_title = (
                    f'Comment thread: "{comment_preview}" ({comment_count} comments)'
                )
            else:
                item_title = f"Comment thread ({comment_count} comments)"
        else:
            # For regular items, use Title() if available
            item_title = (
                obj.Title()
                if hasattr(obj, "Title")
                else getattr(obj, "title", "Unknown")
            )

        # Store metadata about the deletion
        self.storage[item_id] = {
            "id": (
                obj.getId() if hasattr(obj, "getId") else getattr(obj, "id", "unknown")
            ),
            "title": item_title,
            "type": item_type or getattr(obj, "portal_type", "Unknown"),
            "path": original_path,
            "parent_path": "/".join(original_container.getPhysicalPath()),
            "deletion_date": datetime.now(),
            "size": getattr(obj, "get_size", lambda: 0)(),
            "object": obj,  # Store the actual object
        }

        # Check if we need to clean up old items
        self._check_size_limits()

        return item_id

    def get_items(self):
        """Return all items in recycle bin"""
        items = []
        for item_id, data in self.storage.items():
            item_data = data.copy()
            item_data["recycle_id"] = item_id
            # Don't include the actual object in the listing
            if "object" in item_data:
                del item_data["object"]
            items.append(item_data)

        # Sort by deletion date (newest first)
        return sorted(items, key=lambda x: x["deletion_date"], reverse=True)

    def get_item(self, item_id):
        """Get a specific deleted item by ID"""
        return self.storage.get(item_id)

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
        site = self._get_context()
        if target_container is None:
            # Try to get the original parent
            parent_path = item_data["parent_path"]
            try:
                target_container = site.unrestrictedTraverse(parent_path)
            except (KeyError, AttributeError):
                # If original parent doesn't exist, restore to site root
                target_container = site

        # Make sure we don't overwrite existing content
        if obj_id in target_container:
            # Generate a unique ID by appending a timestamp
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            obj_id = f"{obj_id}-restored-{timestamp}"

        # Set the new ID if it was changed
        if obj_id != item_data["id"]:
            obj.id = obj_id

        # Add object to the target container
        target_container._setObject(obj_id, obj)

        # Remove from recycle bin
        del self.storage[item_id]

        restored_obj = target_container[obj_id]
        return restored_obj

    def _restore_comment(self, item_id, item_data, target_container=None):
        """Enhanced restoration method for comments that preserves reply relationships"""
        obj = item_data["object"]
        site = self._get_context()

        # Try to find the original conversation
        parent_path = item_data["parent_path"]
        try:
            conversation = site.unrestrictedTraverse(parent_path)
        except (KeyError, AttributeError):
            # If original conversation doesn't exist, we can't restore the comment
            logger.warning(
                f"Cannot restore comment {item_id}: conversation no longer exists at {parent_path}"
            )
            return None

        # Restore comment back to conversation
        from plone.app.discussion.interfaces import IConversation

        if IConversation.providedBy(conversation):
            # Store the original comment ID before restoration
            original_id = getattr(obj, "comment_id", None)
            original_in_reply_to = getattr(obj, "in_reply_to", None)

            # Track comment relationships using a simple dictionary
            # We won't use annotations directly on the conversation since that causes adaptation issues
            # Instead, we'll use a module-level cache
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

            # Check if the parent comment exists in the conversation (direct or restored)
            if original_in_reply_to is not None and original_in_reply_to != 0:
                parent_found = False

                # First check if it exists directly (not previously deleted)
                if original_in_reply_to in conversation:
                    parent_found = True
                # Then check if it was restored with a different ID
                elif str(original_in_reply_to) in id_mapping:
                    # Use the ID mapping to find the new ID
                    obj.in_reply_to = id_mapping[str(original_in_reply_to)]
                    parent_found = True
                else:
                    # Look through all comments to see if any have the original_id attribute matching our in_reply_to
                    for comment_id in conversation.keys():
                        comment = conversation[comment_id]
                        comment_original_id = getattr(comment, "original_id", None)

                        if comment_original_id is not None and str(
                            comment_original_id
                        ) == str(original_in_reply_to):
                            # We found the parent with a new ID, update the reference
                            obj.in_reply_to = comment_id
                            parent_found = True
                            break

                # If no parent was found, make this a top-level comment
                if not parent_found:
                    obj.in_reply_to = None

            # Store the original ID for future reference
            if not hasattr(obj, "original_id"):
                obj.original_id = original_id

            # When restored, add the comment to the conversation
            new_id = conversation.addComment(obj)

            # Store the mapping of original ID to new ID
            if original_id is not None:
                id_mapping[str(original_id)] = new_id

            # Remove from recycle bin
            del self.storage[item_id]

            # Return the restored comment
            return conversation[new_id]
        else:
            # If the parent is not a conversation, we can't restore
            logger.warning(
                f"Cannot restore comment {item_id}: parent is not a conversation"
            )
            return None

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
            # If original conversation doesn't exist, we can't restore the comment
            logger.warning(
                f"Cannot restore comment tree {item_id}: conversation no longer exists at {parent_path}"
            )
            return None

        # Restore comments back to conversation
        from plone.app.discussion.interfaces import IConversation

        if IConversation.providedBy(conversation):
            # First extract all comments and create a mapping of original IDs
            # to comment objects for quick lookup
            comment_dict = {}
            id_mapping = {}  # Will map original IDs to new IDs

            # Process comments to build reference dictionary
            for comment_obj, _ in comments_to_restore:
                # Store original values we'll need for restoration
                original_id = getattr(comment_obj, "comment_id", None)
                original_in_reply_to = getattr(comment_obj, "in_reply_to", None)

                # Add some debug logging
                logger.info(
                    f"Processing comment with ID: {original_id}, in_reply_to: {original_in_reply_to}"
                )

                # Mark this comment with its original ID for future reference
                if not hasattr(comment_obj, "original_id"):
                    comment_obj.original_id = original_id

                # Store in our dictionary for quick access
                comment_dict[original_id] = {
                    "comment": comment_obj,
                    "in_reply_to": original_in_reply_to,
                }

            # First, try to find the root comment
            root_comment = None
            if root_comment_id in comment_dict:
                root_comment = comment_dict[root_comment_id]["comment"]
                logger.info(f"Found root comment with ID: {root_comment_id}")
            else:
                # Root comment not found by explicit ID, try alternative approaches
                logger.warning(
                    f"Root comment with ID {root_comment_id} not found in comment dictionary"
                )

                # Try to find a top-level comment or one with the lowest ID to use as root
                for comment_id, comment_data in comment_dict.items():
                    in_reply_to = comment_data["in_reply_to"]
                    if in_reply_to == 0 or in_reply_to is None:
                        # Found a top-level comment, use it as root
                        root_comment = comment_data["comment"]
                        root_comment_id = comment_id
                        logger.info(
                            f"Using top-level comment with ID {comment_id} as root"
                        )
                        break

                # If still no root, use the first comment in the dictionary
                if not root_comment and comment_dict:
                    first_key = list(comment_dict.keys())[0]
                    root_comment = comment_dict[first_key]["comment"]
                    root_comment_id = first_key
                    logger.info(
                        f"Using first available comment with ID {first_key} as root"
                    )

            if not root_comment:
                logger.error(
                    f"Cannot restore comment tree {item_id}: no valid root comment could be determined"
                )
                return None

            # If this is a reply to another comment, check if that comment exists
            original_in_reply_to = getattr(root_comment, "in_reply_to", None)
            if original_in_reply_to is not None and original_in_reply_to != 0:
                # Check if parent exists in conversation or needs to be handled specially
                if original_in_reply_to not in conversation:
                    # Look through all comments to see if any were previously this comment's parent
                    parent_found = False
                    for comment_id in conversation.keys():
                        comment = conversation[comment_id]
                        # Check if this comment was previously the parent (by original ID)
                        original_id = getattr(comment, "original_id", None)
                        if original_id == original_in_reply_to:
                            # We found the parent with a new ID, update the reference
                            root_comment.in_reply_to = comment_id
                            parent_found = True
                            logger.info(
                                f"Found existing parent for root comment: {comment_id}"
                            )
                            break

                    # If no parent was found, make this a top-level comment
                    if not parent_found:
                        logger.info(
                            "No parent found for root comment, making it a top-level comment"
                        )
                        root_comment.in_reply_to = None

            # Add the root comment to the conversation
            new_root_id = conversation.addComment(root_comment)
            id_mapping[root_comment_id] = new_root_id
            logger.info(
                f"Added root comment to conversation with new ID: {new_root_id}"
            )

            # Now restore all child comments in order, updating their in_reply_to references
            # Skip the root comment which we've already restored
            remaining_comments = {
                k: v for k, v in comment_dict.items() if k != root_comment_id
            }

            # Keep track of successfully restored comments
            restored_count = 1  # Start with 1 for the root comment

            # Keep trying to restore comments until we can't restore any more
            # We need multiple passes because comments might depend on other comments
            # that haven't been restored yet
            max_passes = 10  # Limit the number of passes to avoid infinite loops
            current_pass = 0

            while remaining_comments and current_pass < max_passes:
                current_pass += 1
                logger.info(
                    f"Pass {current_pass}: {len(remaining_comments)} comments remaining to restore"
                )
                restored_in_pass = 0

                # Copy keys to avoid modifying dict during iteration
                for comment_id in list(remaining_comments.keys()):
                    comment_data = remaining_comments[comment_id]
                    comment = comment_data["comment"]
                    in_reply_to = comment_data["in_reply_to"]

                    # Check if the parent comment has been restored
                    if in_reply_to in id_mapping:
                        # Update reference to the new parent ID
                        comment.in_reply_to = id_mapping[in_reply_to]

                        # Add to conversation
                        new_id = conversation.addComment(comment)
                        id_mapping[comment_id] = new_id

                        # Remove from remaining comments
                        del remaining_comments[comment_id]
                        restored_in_pass += 1
                        logger.info(
                            f"Restored comment {comment_id} with new ID {new_id}, parent {in_reply_to} -> {id_mapping[in_reply_to]}"
                        )

                # If we couldn't restore any comments in this pass, we have an issue
                if restored_in_pass == 0 and remaining_comments:
                    logger.warning(
                        f"Pass {current_pass}: No comments could be restored. "
                        f"{len(remaining_comments)} comments remaining."
                    )
                    # Try one more approach - see if any remaining comments have parents
                    # that don't exist in our mapping but do exist in the conversation
                    for comment_id, comment_data in list(remaining_comments.items()):
                        comment = comment_data["comment"]
                        in_reply_to = comment_data["in_reply_to"]

                        # Check if the parent exists directly in the conversation
                        if in_reply_to and in_reply_to in conversation:
                            comment.in_reply_to = (
                                in_reply_to  # Keep the original reference
                            )
                            new_id = conversation.addComment(comment)
                            id_mapping[comment_id] = new_id
                            del remaining_comments[comment_id]
                            restored_in_pass += 1
                            logger.info(
                                f"Found parent directly in conversation for {comment_id} -> {new_id}"
                            )

                    # If still no progress, make them top-level
                    if restored_in_pass == 0:
                        # Just restore remaining comments as top-level comments
                        logger.warning(
                            f"Some comments in tree {item_id} couldn't be restored with proper relationships. "
                            "Restoring them as top-level comments."
                        )
                        for comment_id, comment_data in remaining_comments.items():
                            comment = comment_data["comment"]
                            comment.in_reply_to = None
                            new_id = conversation.addComment(comment)
                            id_mapping[comment_id] = new_id
                            logger.info(
                                f"Restored comment {comment_id} as top-level comment with new ID {new_id}"
                            )
                        break

                restored_count += restored_in_pass

            # Remove from recycle bin
            del self.storage[item_id]

            # Return the root comment
            logger.info(f"Restored comment tree with {restored_count} comments.")
            return conversation[new_root_id]
        else:
            # If the parent is not a conversation, we can't restore
            logger.warning(
                f"Cannot restore comment tree {item_id}: parent is not a conversation"
            )
            return None

    def purge_item(self, item_id):
        """Permanently delete an item"""
        if item_id not in self.storage:
            return False

        # Simply remove from storage - the object will be garbage collected
        del self.storage[item_id]
        return True

    def purge_expired_items(self):
        """Purge items that exceed the retention period"""
        settings = self._get_settings()
        if not settings.auto_purge:
            return 0

        retention_days = settings.retention_period
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        items_to_purge = []
        for item_id, data in self.storage.items():
            if data["deletion_date"] < cutoff_date:
                items_to_purge.append(item_id)

        purge_count = 0
        for item_id in items_to_purge:
            if self.purge_item(item_id):
                purge_count += 1

        return purge_count

    def _check_size_limits(self):
        """Check if the recycle bin exceeds size limits and purge oldest items if needed"""
        settings = self._get_settings()
        max_size_bytes = settings.maximum_size * 1024 * 1024  # Convert MB to bytes

        total_size = 0
        items_by_date = []

        # Calculate total size and prepare sorted list
        for item_id, data in self.storage.items():
            size = data.get("size", 0)
            total_size += size
            items_by_date.append((item_id, data["deletion_date"], size))

        # Sort by date (oldest first)
        items_by_date.sort(key=lambda x: x[1])

        # Remove oldest items if size limit is exceeded
        while total_size > max_size_bytes and items_by_date:
            item_id, _, size = items_by_date.pop(0)
            if self.purge_item(item_id):
                total_size -= size
                logger.info(f"Purged item {item_id} due to size constraints")
