from datetime import datetime
from plone.base import PloneMessageFactory as _
from plone.base.interfaces.recyclebin import IRecycleBin, IRecycleBinItemForm
from plone.base.utils import human_readable_size
from plone.z3cform import layout
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zExceptions import NotFound
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import logging
import uuid


logger = logging.getLogger(__name__)

class RecycleBinView(form.Form):
    """Form view for recycle bin management"""

    ignoreContext = True
    template = ViewPageTemplateFile("templates/recyclebin.pt")
    
    # Add an ID for the form
    id = "recyclebin-form"
    
    def __init__(self, context, request):
        super().__init__(context, request)
        self.recycle_bin = getUtility(IRecycleBin)

    def update(self):
        super().update()

    @button.buttonAndHandler(_("Restore Selected"), name="restore")
    def handle_restore(self, action):
        """Restore selected items handler"""
        data, errors = self.extractData()

        # Get the selected items from the request directly
        selected_items = self.request.form.get("selected_items", [])
        if not isinstance(selected_items, list):
            selected_items = [selected_items]

        if not selected_items:
            # Improved translation handling
            message = translate(
                _("No items selected for restoration."),
                context=self.request
            )
            IStatusMessage(self.request).addStatusMessage(message, type="info")
            return

        restored_count = 0
        for item_id in selected_items:
            if self.recycle_bin.restore_item(item_id):
                restored_count += 1

        # Improved translation handling with variable mapping
        message = translate(
            _("${count} item(s) restored successfully.", 
              mapping={"count": restored_count}),
            context=self.request
        )
        IStatusMessage(self.request).addStatusMessage(message, type="info")

    @button.buttonAndHandler(_("Delete selected"), name="delete")
    def handle_delete(self, action):
        """Delete selected items handler"""
        data, errors = self.extractData()

        # Get the selected items from the request directly
        selected_items = self.request.form.get("selected_items", [])
        if not isinstance(selected_items, list):
            selected_items = [selected_items]

        if not selected_items:
            # Improved translation handling
            message = translate(
                _("No items selected for deletion."),
                context=self.request
            )
            IStatusMessage(self.request).addStatusMessage(message, type="info")
            return

        deleted_count = 0
        for item_id in selected_items:
            if self.recycle_bin.purge_item(item_id):
                deleted_count += 1

        # Improved translation handling with variable mapping
        message = translate(
            _("${count} item(s) permanently deleted.", 
              mapping={"count": deleted_count}),
            context=self.request
        )
        IStatusMessage(self.request).addStatusMessage(message, type="info")

    @button.buttonAndHandler(_("Empty Recycle Bin"), name="empty")
    def handle_empty(self, action):
        """Empty recycle bin handler"""
        data, errors = self.extractData()

        items = self.recycle_bin.get_items()
        deleted_count = 0

        for item in items:
            item_id = item["recycle_id"]
            if self.recycle_bin.purge_item(item_id):
                deleted_count += 1

        # Improved translation handling with variable mapping
        message = translate(
            _("Recycle bin emptied. ${count} item(s) permanently deleted.", 
              mapping={"count": deleted_count}),
            context=self.request
        )
        IStatusMessage(self.request).addStatusMessage(message, type="info")

    def get_search_query(self):
        """Get the search query from the request"""
        return self.request.form.get("search_query", "")

    def get_sort_option(self):
        """Get the current sort option from the request"""
        return self.request.form.get("sort_by", "date_desc")

    def get_filter_type(self):
        """Get the content type filter from the request"""
        return self.request.form.get("filter_type", "")

    def get_sort_labels(self):
        """Get a dictionary of human-readable sort option labels"""
        return {
            "date_desc": _("Newest first (default)"),
            "date_asc": _("Oldest first"),
            "title_asc": _("Title (A-Z)"),
            "title_desc": _("Title (Z-A)"),
            "type_asc": _("Type (A-Z)"),
            "type_desc": _("Type (Z-A)"),
            "path_asc": _("Path (A-Z)"),
            "path_desc": _("Path (Z-A)"),
            "size_asc": _("Size (smallest first)"),
            "size_desc": _("Size (largest first)"),
        }

    def get_clear_url(self, param_to_remove):
        """Generate a URL that clears a specific filter parameter while preserving others

        Args:
            param_to_remove: The parameter name to remove from the URL

        Returns:
            URL string with the specified parameter removed
        """
        base_url = f"{self.context.absolute_url()}/@@recyclebin"
        params = []

        # Add search query if it exists and is not being removed
        if param_to_remove != "search_query" and self.get_search_query():
            params.append(f"search_query={self.get_search_query()}")

        # Add filter type if it exists and is not being removed
        if param_to_remove != "filter_type" and self.get_filter_type():
            params.append(f"filter_type={self.get_filter_type()}")

        # Add sort option if it exists, is not default, and is not being removed
        sort_option = self.get_sort_option()
        if param_to_remove != "sort_by" and sort_option != "date_desc":
            params.append(f"sort_by={sort_option}")

        # Construct final URL
        if params:
            return f"{base_url}?{'&'.join(params)}"
        return base_url

    def get_available_types(self, items):
        """Get a list of all content types present in the recycle bin"""
        types = set()
        for item in items:
            item_type = item.get("type")
            if item_type:
                types.add(item_type)
        return sorted(list(types))

    def get_items(self):
        """Get all items in the recycle bin"""
        items = self.recycle_bin.get_items()

        # Create a list of all items that are children of a parent in the recycle bin
        child_items_to_exclude = []
        for item in items:
            # If this item is a parent with children, add its children to exclusion list
            if "children" in item:
                for child_id in item.get("children", {}):
                    child_items_to_exclude.append(child_id)

        logger.debug(f"Child items to exclude: {child_items_to_exclude}")

        # Only include items that are not children of other recycled items
        items = [item for item in items if item.get("id") not in child_items_to_exclude]

        # For comments, add extra information about the content they belong to
        for item in items:
            if item.get("type") == "Discussion Item":
                # Extract content path from comment path
                path = item.get("path", "")
                # The conversation part is usually ++conversation++default
                parts = path.split("++conversation++")
                if len(parts) > 1:
                    content_path = parts[0]
                    # Remove trailing slash if present
                    if content_path.endswith("/"):
                        content_path = content_path[:-1]
                    item["content_path"] = content_path

                    # Try to get the content title
                    try:
                        content = self.context.unrestrictedTraverse(content_path)
                        item["content_title"] = content.Title()
                    except (KeyError, AttributeError):
                        # Use translation for missing content
                        item["content_title"] = translate(
                            _("Content no longer exists"), 
                            context=self.request
                        )

        # Apply content type filtering if specified
        filter_type = self.get_filter_type()
        if filter_type:
            items = [item for item in items if item.get("type") == filter_type]

        # Filter items based on search query
        search_query = self.get_search_query().lower()
        if search_query:
            filtered_items = []
            items_with_matching_children = []

            for item in items:
                # Search in title
                if search_query in item.get("title", "").lower():
                    filtered_items.append(item)
                    continue

                # Search in path
                if search_query in item.get("path", "").lower():
                    filtered_items.append(item)
                    continue

                # Search in parent path
                if search_query in item.get("parent_path", "").lower():
                    filtered_items.append(item)
                    continue

                # Search in ID
                if search_query in item.get("id", "").lower():
                    filtered_items.append(item)
                    continue

                # Search in type
                if search_query in item.get("type", "").lower():
                    filtered_items.append(item)
                    continue

                # Search in children if this item has children
                if "children" in item and isinstance(item["children"], dict):
                    child_matches = []

                    for child_id, child_data in item["children"].items():
                        # Check each child for matches
                        child_matches_query = False

                        # Check in title
                        if search_query in child_data.get("title", "").lower():
                            child_matches_query = True
                        # Check in path
                        elif search_query in child_data.get("path", "").lower():
                            child_matches_query = True
                        # Check in ID
                        elif search_query in child_data.get("id", "").lower():
                            child_matches_query = True
                        # Check in type
                        elif search_query in child_data.get("type", "").lower():
                            child_matches_query = True

                        # Add to matches if found
                        if child_matches_query:
                            child_matches.append(child_data)

                    # If any children match, mark the parent item
                    if child_matches:
                        # Make a copy of the item so we don't modify the original
                        parent_item = item.copy()
                        parent_item["matching_children"] = child_matches
                        parent_item["matching_children_count"] = len(child_matches)
                        items_with_matching_children.append(parent_item)

            # Combine direct matches with items that have matching children
            # Direct matches come first
            items = filtered_items + items_with_matching_children

        # Apply sorting
        sort_option = self.get_sort_option()
        if sort_option == "title_asc":
            items.sort(key=lambda x: x.get("title", "").lower())
        elif sort_option == "title_desc":
            items.sort(key=lambda x: x.get("title", "").lower(), reverse=True)
        elif sort_option == "type_asc":
            items.sort(key=lambda x: x.get("type", "").lower())
        elif sort_option == "type_desc":
            items.sort(key=lambda x: x.get("type", "").lower(), reverse=True)
        elif sort_option == "path_asc":
            items.sort(key=lambda x: x.get("path", "").lower())
        elif sort_option == "path_desc":
            items.sort(key=lambda x: x.get("path", "").lower(), reverse=True)
        elif sort_option == "size_asc":
            items.sort(key=lambda x: x.get("size", 0))
        elif sort_option == "size_desc":
            items.sort(key=lambda x: x.get("size", 0), reverse=True)
        elif sort_option == "date_asc":
            items.sort(key=lambda x: x.get("deletion_date", datetime.now()))
        # Default: date_desc
        else:
            items.sort(
                key=lambda x: x.get("deletion_date", datetime.now()), reverse=True
            )

        return items

    def format_size(self, size_bytes):
        """Format size in bytes to human-readable format"""
        return human_readable_size(size_bytes)


@implementer(IPublishTraverse)
class RecycleBinItemView(form.Form):
    """View for managing individual recycled items"""

    ignoreContext = True
    template = ViewPageTemplateFile("templates/recyclebin_item.pt")
    item_id = None
    fields = field.Fields(IRecycleBinItemForm)
    
    def __init__(self, context, request):
        super().__init__(context, request)
        self.recycle_bin = getUtility(IRecycleBin)

    def publishTraverse(self, request, name):
        """Handle URLs like /recyclebin-item/[item_id]"""
        logger.info(f"RecycleBinItemView.publishTraverse called with name: {name}")
        if self.item_id is None:  # First traversal
            self.item_id = name
            logger.info(f"Set item_id to: {self.item_id}")
            return self
        logger.warning(f"Additional traversal attempted with name: {name}")
        raise NotFound(self, name, request)

    def updateWidgets(self):
        super().updateWidgets()

    def update(self):
        super().update()

        # Check if we have a valid item before proceeding
        if self.item_id is None:
            logger.warning("No item_id set, redirecting to main recyclebin view")
            self.request.response.redirect(f"{self.context.absolute_url()}/@@recyclebin")
            return

        # Handle restoration of children
        if "restore.child" in self.request.form:
            self._handle_child_restoration()

    @button.buttonAndHandler(_("Restore item"), name="restore")
    def handle_restore(self, action):
        """Restore this item"""
        data, errors = self.extractData()
        if errors:
            return

        # Get target container if specified
        target_path = data.get("target_container", "")
        target_container = None

        if target_path:
            try:
                target_container = self.context.unrestrictedTraverse(target_path)
            except (KeyError, AttributeError):
                # Using the improved translation pattern
                message = translate(
                    _("Target location not found: ${path}", 
                      mapping={"path": target_path}),
                    context=self.request
                )
                IStatusMessage(self.request).addStatusMessage(message, type="error")
                return

        # Restore the item
        item = self.get_item()
        if not item:
            # Using the improved translation pattern
            message = translate(
                _("Item not found. It may have been already restored or deleted."),
                context=self.request
            )
            IStatusMessage(self.request).addStatusMessage(message, type="error")
            self.request.response.redirect(f"{self.context.absolute_url()}/@@recyclebin")
            return

        restored_obj = self.recycle_bin.restore_item(self.item_id, target_container)

        if restored_obj:
            # Using the improved translation pattern
            message = translate(
                _("Item '${title}' successfully restored.", 
                  mapping={"title": restored_obj.Title()}),
                context=self.request
            )
            IStatusMessage(self.request).addStatusMessage(message, type="info")
            self.request.response.redirect(restored_obj.absolute_url())
        else:
            # Using the improved translation pattern
            message = translate(
                _("Failed to restore item. It may have been already restored or deleted."),
                context=self.request
            )
            IStatusMessage(self.request).addStatusMessage(message, type="error")
            self.request.response.redirect(f"{self.context.absolute_url()}/@@recyclebin")

    @button.buttonAndHandler(_("Permanently delete"), name="delete")
    def handle_delete(self, action):
        """Permanently delete this item"""
        data, errors = self.extractData()

        # Get item info before deletion
        item = self.get_item()
        if item:
            item_title = item.get("title", "Unknown")

            if self.recycle_bin.purge_item(self.item_id):
                # Using the improved translation pattern
                message = translate(
                    _("Item '${title}' permanently deleted.", 
                      mapping={"title": item_title}),
                    context=self.request
                )
                IStatusMessage(self.request).addStatusMessage(message, type="info")
            else:
                # Using the improved translation pattern
                message = translate(
                    _("Failed to delete item '${title}'.", 
                      mapping={"title": item_title}),
                    context=self.request
                )
                IStatusMessage(self.request).addStatusMessage(message, type="error")
        else:
            # Using the improved translation pattern
            message = translate(
                _("Item not found. It may have been already deleted."),
                context=self.request
            )
            IStatusMessage(self.request).addStatusMessage(message, type="error")

        self.request.response.redirect(f"{self.context.absolute_url()}/@@recyclebin")

    def _handle_child_restoration(self):
        """Extract child restoration logic to separate method for clarity"""
        child_id = self.request.form.get("child_id")
        target_path = self.request.form.get("target_path")

        if child_id and target_path:
            try:
                # Get item data
                item_data = self.recycle_bin.get_item(self.item_id)

                if item_data and "children" in item_data:
                    child_data = item_data["children"].get(child_id)
                    if child_data:
                        # Try to get target container
                        try:
                            target_container = self.context.unrestrictedTraverse(target_path)

                            # Create a temporary storage entry for the child
                            temp_id = str(uuid.uuid4())
                            self.recycle_bin.storage[temp_id] = child_data

                            # Restore the child
                            restored_obj = self.recycle_bin.restore_item(temp_id, target_container)

                            if restored_obj:
                                # Remove child from parent's children dict
                                del item_data["children"][child_id]
                                item_data["children_count"] = len(item_data["children"])

                                # Using the improved translation pattern
                                message = translate(
                                    _("Child item '${title}' successfully restored.", 
                                      mapping={"title": child_data['title']}),
                                    context=self.request
                                )
                                IStatusMessage(self.request).addStatusMessage(message, type="info")
                                self.request.response.redirect(restored_obj.absolute_url())
                                return
                        except (KeyError, AttributeError):
                            # Using the improved translation pattern
                            message = translate(
                                _("Target location not found: ${path}", 
                                  mapping={"path": target_path}),
                                context=self.request
                            )
                            IStatusMessage(self.request).addStatusMessage(message, type="error")
            except Exception as e:
                logger.error(f"Error restoring child item: {e}")
                # Using the improved translation pattern
                message = translate(
                    _("Failed to restore child item."),
                    context=self.request
                )
                IStatusMessage(self.request).addStatusMessage(message, type="error")

    def get_item(self):
        """Get the specific recycled item"""
        logger.info(f"RecycleBinItemView.get_item called for ID: {self.item_id}")
        if not self.item_id:
            logger.warning("get_item called with no item_id")
            return None

        item = self.recycle_bin.get_item(self.item_id)
        if item is None:
            logger.warning(f"No item found in recycle bin with ID: {self.item_id}")
        else:
            logger.info(f"Found item: {item.get('title', 'Unknown')} of type {item.get('type', 'Unknown')}")
        return item

    def get_children(self):
        """Get the children of this item if it's a folder or collection"""
        item = self.get_item()
        if item and "children" in item:
            children = []
            for child_id, child_data in item["children"].items():
                # Don't include the actual object in the listing
                child_info = child_data.copy()
                if "object" in child_info:
                    del child_info["object"]
                children.append(child_info)
            return children
        return []

    def get_comment_children(self):
        """Get comments from a CommentTree item"""
        item = self.get_item()
        if item and item.get("type") == "CommentTree":
            comment_tree = item.get("object", {})
            comments = comment_tree.get("comments", [])

            # Process comments to build a list for display
            comment_list = []
            for comment_obj, comment_path in comments:
                # Get author info
                author = getattr(comment_obj, 'author_name', None) or getattr(comment_obj, 'author_username', 'Anonymous')
                
                # Extract comment data
                comment_data = {
                    "id": getattr(comment_obj, "comment_id", ""),
                    "text": getattr(comment_obj, "text", ""),
                    "author": author,
                    "in_reply_to": getattr(comment_obj, "in_reply_to", None),
                    "path": comment_path,
                    "creation_date": getattr(comment_obj, "creation_date", None),
                    "modification_date": getattr(comment_obj, "modification_date", None),
                    # Using the improved translation pattern
                    "title": translate(
                        _("Comment by ${author}", 
                          mapping={"author": author}),
                        context=self.request
                    ),
                    "size": len(getattr(comment_obj, "text", "")),
                }
                comment_list.append(comment_data)

            return comment_list
        return []

    def format_size(self, size_bytes):
        """Format size in bytes to human-readable format"""
        return human_readable_size(size_bytes)


class RecycleBinEnabled(BrowserView):
    """View to check if the recycle bin is enabled"""
    
    def __call__(self):
        """Return True if the recycle bin is enabled, False otherwise"""
        recycle_bin = getUtility(IRecycleBin)
        return recycle_bin.is_enabled()
