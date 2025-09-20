from datetime import datetime
from plone.base import PloneMessageFactory as _
from plone.base.interfaces.recyclebin import IRecycleBin
from plone.base.interfaces.recyclebin import IRecycleBinItemForm
from plone.base.utils import human_readable_size
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zExceptions import NotFound
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.i18n import translate
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import logging
import uuid


logger = logging.getLogger(__name__)


def _is_error_result(result):
    """Helper method to check if a result is an error dictionary

    Args:
        result: The result to check

    Returns:
        Boolean indicating if the result is an error dictionary
    """
    return isinstance(result, dict) and not result.get("success", True)





class RecycleBinView(form.Form):
    """Form view for recycle bin management"""

    ignoreContext = True
    template = ViewPageTemplateFile("templates/recyclebin.pt")

    # Add an ID for the form
    id = "recyclebin-form"

    def __init__(self, context, request):
        super().__init__(context, request)
        self.recycle_bin = getUtility(IRecycleBin)

    @button.buttonAndHandler(_("Restore Selected"), name="restore")
    def handle_restore(self, action):
        """Restore selected items handler"""
        data, errors = self.extractData()

        # Get the selected items from the request directly
        selected_items = self.request.form.get("selected_items", [])
        if not isinstance(selected_items, list):
            selected_items = [selected_items]

        if not selected_items:
            message = translate(
                _("No items selected for restoration."), context=self.request
            )
            IStatusMessage(self.request).addStatusMessage(message, type="info")
            return

        restored_count = 0
        missing_parents_count = 0
        missing_parent_items = []

        for item_id in selected_items:
            result = self.recycle_bin.restore_item(item_id)

            # Handle different types of return values
            if _is_error_result(result):
                # This is a failed restoration with an error message
                missing_parents_count += 1
                # Get the item title for better user feedback
                item_data = self.recycle_bin.get_item(item_id)
                if item_data:
                    missing_parent_items.append(
                        {
                            "id": item_id,
                            "title": item_data.get("title", "Unknown"),
                            "parent_path": item_data.get("parent_path", "Unknown"),
                            "error": result.get("error", "Unknown error"),
                        }
                    )
            elif result:
                # Successful restoration
                restored_count += 1

        # Success message for restored items
        if restored_count > 0:
            message = translate(
                _(
                    "${count} item(s) restored successfully.",
                    mapping={"count": restored_count},
                ),
                context=self.request,
            )
            IStatusMessage(self.request).addStatusMessage(message, type="info")

        # Error message for items with missing parents
        if missing_parents_count > 0:
            if len(missing_parent_items) == 1:
                # Single item message
                item = missing_parent_items[0]
                message = translate(
                    _(
                        "The item '${title}' could not be restored because its original location no longer exists. "
                        "Please choose a different location.",
                        mapping={"title": item["title"]},
                    ),
                    context=self.request,
                )
                # Redirect to the item's detail page if only one item had this issue
                self.request.response.redirect(
                    f"{self.context.absolute_url()}/@@recyclebin-item/{item['id']}"
                )
            else:
                # Multiple items message
                message = translate(
                    _(
                        "${count} items could not be restored because their original locations no longer exist. "
                        "Please visit each item's detail page to specify a new location.",
                        mapping={"count": missing_parents_count},
                    ),
                    context=self.request,
                )

            IStatusMessage(self.request).addStatusMessage(message, type="error")

    @button.buttonAndHandler(_("Delete selected"), name="delete")
    def handle_delete(self, action):
        """Delete selected items handler"""
        data, errors = self.extractData()

        # Get the selected items from the request directly
        selected_items = self.request.form.get("selected_items", [])
        if not isinstance(selected_items, list):
            selected_items = [selected_items]

        if not selected_items:
            message = translate(
                _("No items selected for deletion."), context=self.request
            )
            IStatusMessage(self.request).addStatusMessage(message, type="info")
            return

        deleted_count = 0
        for item_id in selected_items:
            if self.recycle_bin.purge_item(item_id):
                deleted_count += 1

        message = translate(
            _(
                "${count} item(s) permanently deleted.",
                mapping={"count": deleted_count},
            ),
            context=self.request,
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

        message = translate(
            _(
                "Recycle bin emptied. ${count} item(s) permanently deleted.",
                mapping={"count": deleted_count},
            ),
            context=self.request,
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

    def _check_item_matches_search(self, item, search_query):
        """Check if an item matches the search query.

        Args:
            item: The item to check
            search_query: The search query string (lowercase)

        Returns:
            Boolean indicating if the item matches
        """
        # Search in title
        if search_query in item.get("title", "").lower():
            return True

        # Search in path
        if search_query in item.get("path", "").lower():
            return True

        # Search in parent path
        if search_query in item.get("parent_path", "").lower():
            return True

        # Search in ID
        if search_query in item.get("id", "").lower():
            return True

        # Search in type
        if search_query in item.get("type", "").lower():
            return True

        return False

    def _find_matching_children(self, item, search_query):
        """Find children of an item that match the search query.

        Args:
            item: The parent item to check children of
            search_query: The search query string (lowercase)

        Returns:
            List of matching children or None if no matches
        """
        if "children" in item and isinstance(item["children"], dict):
            child_matches = []

            for child_id, child_data in item["children"].items():
                # Check each child for matches
                if (
                    search_query in child_data.get("title", "").lower()
                    or search_query in child_data.get("path", "").lower()
                    or search_query in child_data.get("id", "").lower()
                    or search_query in child_data.get("type", "").lower()
                ):
                    child_matches.append(child_data)

            if child_matches:
                return child_matches

        return None

    def _process_comment_item(self, item):
        """Add extra information to comment items.

        Args:
            item: The comment item to process
        """
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
                    item["content_title"] = translate(
                        _("Content no longer exists"), context=self.request
                    )

    def _apply_sorting(self, items, sort_option):
        """Apply sorting to the items list.

        Args:
            items: List of items to sort
            sort_option: The sort option to apply

        Returns:
            Sorted list of items
        """
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

    def _check_parent_exists(self, item):
        """Check if the parent container of an item exists

        Args:
            item: The item to check

        Returns:
            Boolean indicating if the parent container exists
        """
        # Comments and comment trees have special handling
        if item.get("type") in ("CommentTree", "Discussion Item"):
            return True

        site = getSite()
        parent_path = item.get("parent_path", "")

        if not parent_path:
            return False

        try:
            parent = site.unrestrictedTraverse(parent_path)
            return parent is not None
        except (KeyError, AttributeError):
            return False

    def get_items(self):
        """Get all items in the recycle bin"""
        items = self.recycle_bin.get_items()

        # Get filters early to avoid multiple lookups during the loop
        filter_type = self.get_filter_type()
        search_query = self.get_search_query().lower()

        # Create a list of all items that are children of a parent in the recycle bin
        child_items_to_exclude = []
        for item in items:
            # If this item is a parent with children, add its children to exclusion list
            if "children" in item:
                for child_id in item.get("children", {}):
                    child_items_to_exclude.append(child_id)

        logger.debug(f"Child items to exclude: {child_items_to_exclude}")

        # Process items with direct matches
        filtered_items = []
        items_with_matching_children = []

        for item in items:
            if item.get("id") not in child_items_to_exclude:
                # Apply type filtering
                if filter_type and item.get("type") != filter_type:
                    continue

                # Check if parent container exists and add flag to the item
                item["parent_exists"] = self._check_parent_exists(item)

                # Add comment-specific information
                self._process_comment_item(item)

                # Apply search query filtering
                if search_query:
                    # Check for direct matches
                    if self._check_item_matches_search(item, search_query):
                        filtered_items.append(item)
                        continue

                    # Check for matches in children
                    matching_children = self._find_matching_children(item, search_query)
                    if matching_children:
                        # Make a copy of the item so we don't modify the original
                        parent_item = item.copy()
                        parent_item["matching_children"] = matching_children
                        parent_item["matching_children_count"] = len(matching_children)
                        items_with_matching_children.append(parent_item)
                else:
                    # No search query, include all items
                    filtered_items.append(item)

        # Combine results based on whether we're searching or not
        if search_query:
            items = filtered_items + items_with_matching_children
        else:
            items = filtered_items

        # Apply sorting
        return self._apply_sorting(items, self.get_sort_option())

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
        logger.debug(f"RecycleBinItemView.publishTraverse called with name: {name}")
        if self.item_id is None:  # First traversal
            self.item_id = name
            logger.debug(f"Set item_id to: {self.item_id}")
            return self
        logger.debug(f"Additional traversal attempted with name: {name}")
        raise NotFound(self, name, request)

    def update(self):
        super().update()

        # Check if we have a valid item before proceeding
        if self.item_id is None:
            logger.debug("No item_id set, redirecting to main recyclebin view")
            self.request.response.redirect(
                f"{self.context.absolute_url()}/@@recyclebin"
            )
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

                message = translate(
                    _(
                        "The folder '${path}' where you are trying to restore this item cannot be found. It may have been moved or deleted. Please choose a different location.",
                        mapping={"path": target_path},
                    ),
                    context=self.request,
                )
                IStatusMessage(self.request).addStatusMessage(message, type="error")
                return

        # Restore the item
        item = self.get_item()
        if not item:
            message = translate(
                _("Item not found. It may have been already restored or deleted."),
                context=self.request,
            )
            IStatusMessage(self.request).addStatusMessage(message, type="error")
            self.request.response.redirect(
                f"{self.context.absolute_url()}/@@recyclebin"
            )
            return

        result = self.recycle_bin.restore_item(self.item_id, target_container)

        # Check if we got an error dictionary using helper method
        if _is_error_result(result):
            # Show the error message
            error_message = result.get(
                "error", "Unknown error occurred during restoration"
            )
            IStatusMessage(self.request).addStatusMessage(error_message, type="error")

            # Redirect back to the item view to allow selecting a different target
            self.request.response.redirect(
                f"{self.context.absolute_url()}/@@recyclebin-item/{self.item_id}"
            )
            return

        restored_obj = result

        if restored_obj:

            message = translate(
                _(
                    "Item '${title}' successfully restored.",
                    mapping={"title": restored_obj.Title()},
                ),
                context=self.request,
            )
            IStatusMessage(self.request).addStatusMessage(message, type="info")

            # Determine the appropriate URL to redirect to after restoration
            context_state = getMultiAdapter(
                (restored_obj, self.request), name="plone_context_state"
            )
            redirect_url = context_state.view_url()

            self.request.response.redirect(redirect_url)
        else:

            message = translate(
                _(
                    "Failed to restore item. It may have been already restored or deleted."
                ),
                context=self.request,
            )
            IStatusMessage(self.request).addStatusMessage(message, type="error")
            self.request.response.redirect(
                f"{self.context.absolute_url()}/@@recyclebin"
            )

    @button.buttonAndHandler(_("Permanently delete"), name="delete")
    def handle_delete(self, action):
        """Permanently delete this item"""
        data, errors = self.extractData()

        # Get item info before deletion
        item = self.get_item()
        if item:
            item_title = item.get("title", "Unknown")

            if self.recycle_bin.purge_item(self.item_id):

                message = translate(
                    _(
                        "Item '${title}' permanently deleted.",
                        mapping={"title": item_title},
                    ),
                    context=self.request,
                )
                IStatusMessage(self.request).addStatusMessage(message, type="info")
            else:

                message = translate(
                    _(
                        "Failed to delete item '${title}'.",
                        mapping={"title": item_title},
                    ),
                    context=self.request,
                )
                IStatusMessage(self.request).addStatusMessage(message, type="error")
        else:

            message = translate(
                _("Item not found. It may have been already deleted."),
                context=self.request,
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
                            target_container = self.context.unrestrictedTraverse(
                                target_path
                            )

                            # Create a temporary storage entry for the child
                            temp_id = str(uuid.uuid4())
                            self.recycle_bin.storage[temp_id] = child_data

                            # Restore the child
                            result = self.recycle_bin.restore_item(
                                temp_id, target_container
                            )

                            # Check if we got an error dictionary
                            if _is_error_result(result):
                                error_message = result.get(
                                    "error", "Unknown error during child restoration"
                                )
                                IStatusMessage(self.request).addStatusMessage(
                                    error_message, type="error"
                                )
                                return

                            restored_obj = result

                            if restored_obj:
                                # Remove child from parent's children dict
                                del item_data["children"][child_id]
                                item_data["children_count"] = len(item_data["children"])

                                message = translate(
                                    _(
                                        "Child item '${title}' successfully restored.",
                                        mapping={"title": child_data["title"]},
                                    ),
                                    context=self.request,
                                )
                                IStatusMessage(self.request).addStatusMessage(
                                    message, type="info"
                                )
                                self.request.response.redirect(
                                    restored_obj.absolute_url()
                                )
                                return
                        except (KeyError, AttributeError):

                            message = translate(
                                _(
                                    "Target location not found: ${path}",
                                    mapping={"path": target_path},
                                ),
                                context=self.request,
                            )
                            IStatusMessage(self.request).addStatusMessage(
                                message, type="error"
                            )
            except Exception as e:
                logger.error(f"Error restoring child item: {e}")

                message = translate(
                    _("Failed to restore child item."), context=self.request
                )
                IStatusMessage(self.request).addStatusMessage(message, type="error")

    def get_item(self):
        """Get the specific recycled item"""
        logger.debug(f"RecycleBinItemView.get_item called for ID: {self.item_id}")
        if not self.item_id:
            logger.debug("get_item called with no item_id")
            return None

        item = self.recycle_bin.get_item(self.item_id)
        if item is None:
            logger.debug(f"No item found in recycle bin with ID: {self.item_id}")
        else:
            logger.debug(
                f"Found item: {item.get('title', 'Unknown')} of type {item.get('type', 'Unknown')}"
            )
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
                author = getattr(comment_obj, "author_name", None) or getattr(
                    comment_obj, "author_username", "Anonymous"
                )

                # Extract comment data
                comment_data = {
                    "id": getattr(comment_obj, "comment_id", ""),
                    "text": getattr(comment_obj, "text", ""),
                    "author": author,
                    "in_reply_to": getattr(comment_obj, "in_reply_to", None),
                    "path": comment_path,
                    "creation_date": getattr(comment_obj, "creation_date", None),
                    "modification_date": getattr(
                        comment_obj, "modification_date", None
                    ),
                    "title": translate(
                        _("Comment by ${author}", mapping={"author": author}),
                        context=self.request,
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
