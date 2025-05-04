from datetime import datetime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.recyclebin import IRecycleBin
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zExceptions import NotFound
from zope import schema
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse

import logging
import uuid


logger = logging.getLogger(__name__)


# Utility functions to avoid code duplication
def format_date(context, date):
    """Format date for display"""
    if date is None:
        return ""
    portal = getToolByName(context, "portal_url").getPortalObject()
    return portal.restrictedTraverse("@@plone").toLocalizedTime(date, long_format=True)


def format_size(size_bytes):
    """Format size in bytes to human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


class IRecycleBinForm(Interface):
    """Schema for the recycle bin form"""

    selected_items = schema.List(
        title="Selected Items",
        description="Selected items for operations",
        value_type=schema.TextLine(),
        required=False,
    )


class RecycleBinForm(form.Form):
    """Form for the recycle bin operations"""

    ignoreContext = True
    schema = IRecycleBinForm

    # Don't need fields as we'll just use the template's checkboxes
    # and handle the extraction manually

    @button.buttonAndHandler("Restore Selected", name="restore")
    def handle_restore(self, action):
        """Restore selected items handler"""
        data, errors = self.extractData()

        # Get the selected items from the request directly
        selected_items = self.request.form.get("selected_items", [])
        if not isinstance(selected_items, list):
            selected_items = [selected_items]

        if not selected_items:
            IStatusMessage(self.request).addStatusMessage(
                "No items selected for restoration.", type="info"
            )
            return

        recycle_bin = getUtility(IRecycleBin)
        restored_count = 0
        for item_id in selected_items:
            if recycle_bin.restore_item(item_id):
                restored_count += 1

        message = f"{restored_count} item{'s' if restored_count != 1 else ''} restored successfully."
        IStatusMessage(self.request).addStatusMessage(message, type="info")

    @button.buttonAndHandler("Delete selected", name="delete")
    def handle_delete(self, action):
        """Delete selected items handler"""
        data, errors = self.extractData()

        # Get the selected items from the request directly
        selected_items = self.request.form.get("selected_items", [])
        if not isinstance(selected_items, list):
            selected_items = [selected_items]

        if not selected_items:
            IStatusMessage(self.request).addStatusMessage(
                "No items selected for deletion.", type="info"
            )
            return

        recycle_bin = getUtility(IRecycleBin)
        deleted_count = 0
        for item_id in selected_items:
            if recycle_bin.purge_item(item_id):
                deleted_count += 1

        message = f"{deleted_count} item{'s' if deleted_count != 1 else ''} permanently deleted."
        IStatusMessage(self.request).addStatusMessage(message, type="info")

    @button.buttonAndHandler("Empty Recycle Bin", name="empty")
    def handle_empty(self, action):
        """Empty recycle bin handler"""
        data, errors = self.extractData()

        recycle_bin = getUtility(IRecycleBin)
        items = recycle_bin.get_items()
        deleted_count = 0

        for item in items:
            item_id = item["recycle_id"]
            if recycle_bin.purge_item(item_id):
                deleted_count += 1

        message = f"Recycle bin emptied. {deleted_count} item{'s' if deleted_count != 1 else ''} permanently deleted."
        IStatusMessage(self.request).addStatusMessage(message, type="info")


class RecycleBinView(BrowserView):
    """Browser view for recycle bin management"""

    template = ViewPageTemplateFile("templates/recyclebin.pt")

    def __call__(self):
        # Initialize form
        form = RecycleBinForm(self.context, self.request)
        form.update()

        # Check if form was submitted and return template
        return self.template()

    def get_recycle_bin(self):
        """Get the recycle bin utility"""
        return getUtility(IRecycleBin)

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
            "date_desc": "Newest first (default)",
            "date_asc": "Oldest first",
            "title_asc": "Title (A-Z)",
            "title_desc": "Title (Z-A)",
            "type_asc": "Type (A-Z)",
            "type_desc": "Type (Z-A)",
            "path_asc": "Path (A-Z)",
            "path_desc": "Path (Z-A)",
            "size_asc": "Size (smallest first)",
            "size_desc": "Size (largest first)",
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
        recycle_bin = self.get_recycle_bin()
        items = recycle_bin.get_items()

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
                        item["content_title"] = "Content no longer exists"

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

    def format_date(self, date):
        """Format date for display"""
        return format_date(self.context, date)

    def format_size(self, size_bytes):
        """Format size in bytes to human-readable format"""
        return format_size(size_bytes)


class IRecycleBinItemForm(Interface):
    """Schema for the recycle bin item form"""

    target_container = schema.TextLine(
        title="Target container",
        description="Path to container where the item should be restored (optional)",
        required=False,
    )


class RecycleBinItemForm(form.Form):
    """Form for managing individual recycled items"""

    ignoreContext = True
    fields = field.Fields(IRecycleBinItemForm)

    def __init__(self, context, request, item_id=None):
        super().__init__(context, request)
        self.item_id = item_id
        self.recycle_bin = getUtility(IRecycleBin)
        self.item = None
        if self.item_id:
            self.item = self.recycle_bin.get_item(self.item_id)

    @button.buttonAndHandler("Restore item", name="restore")
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
                message = f"Target location not found: {target_path}"
                IStatusMessage(self.request).addStatusMessage(message, type="error")
                return

        # Restore the item
        restored_obj = self.recycle_bin.restore_item(self.item_id, target_container)

        if restored_obj:
            message = f"Item '{restored_obj.Title()}' successfully restored."
            IStatusMessage(self.request).addStatusMessage(message, type="info")
            self.request.response.redirect(restored_obj.absolute_url())
        else:
            message = (
                "Failed to restore item. It may have been already restored or deleted."
            )
            IStatusMessage(self.request).addStatusMessage(message, type="error")
            self.request.response.redirect(
                f"{self.context.absolute_url()}/@@recyclebin"
            )

    @button.buttonAndHandler("Permanently delete", name="delete")
    def handle_delete(self, action):
        """Permanently delete this item"""
        data, errors = self.extractData()

        # Get item info before deletion
        if self.item:
            item_title = self.item.get("title", "Unknown")

            if self.recycle_bin.purge_item(self.item_id):
                message = f"Item '{item_title}' permanently deleted."
                IStatusMessage(self.request).addStatusMessage(message, type="info")
            else:
                message = f"Failed to delete item '{item_title}'."
                IStatusMessage(self.request).addStatusMessage(message, type="error")
        else:
            message = "Item not found. It may have been already deleted."
            IStatusMessage(self.request).addStatusMessage(message, type="error")

        self.request.response.redirect(f"{self.context.absolute_url()}/@@recyclebin")


@implementer(IPublishTraverse)
class RecycleBinItemView(BrowserView):
    """View for managing individual recycled items"""

    template = ViewPageTemplateFile("templates/recyclebin_item.pt")
    item_id = None

    def publishTraverse(self, request, name):
        """Handle URLs like /recyclebin/item/[item_id]"""
        logger.info(f"RecycleBinItemView.publishTraverse called with name: {name}")
        if self.item_id is None:  # First traversal
            self.item_id = name
            logger.info(f"Set item_id to: {self.item_id}")
            return self
        logger.warning(f"Additional traversal attempted with name: {name}")
        raise NotFound(self, name, request)

    def __call__(self):
        """Handle item operations"""
        logger.info(f"RecycleBinItemView.__call__ started with item_id: {self.item_id}")
        if self.item_id is None:
            logger.warning("No item_id set, redirecting to main recyclebin view")
            self.request.response.redirect(
                f"{self.context.absolute_url()}/@@recyclebin"
            )
            return ""

        # Handle restoration of children
        if "restore.child" in self.request.form:
            self._handle_child_restoration()

        # Initialize and update the form
        form = RecycleBinItemForm(self.context, self.request, self.item_id)
        form.update()

        # Get the item before rendering template
        item = self.get_item()
        if item is None:
            logger.warning(
                f"No item found with ID: {self.item_id}, redirecting to main `recyclebin` view"
            )
            self.request.response.redirect(
                f"{self.context.absolute_url()}/@@recyclebin"
            )
            return ""

        logger.info(f"Found item with title: {item.get('title', 'Unknown')}")
        return self.template()

    def _handle_child_restoration(self):
        """Extract child restoration logic to separate method for clarity"""
        child_id = self.request.form.get("child_id")
        target_path = self.request.form.get("target_path")

        if child_id and target_path:
            try:
                # Get item data
                recycle_bin = getUtility(IRecycleBin)
                item_data = recycle_bin.get_item(self.item_id)

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
                            recycle_bin.storage[temp_id] = child_data

                            # Restore the child
                            restored_obj = recycle_bin.restore_item(
                                temp_id, target_container
                            )

                            if restored_obj:
                                # Remove child from parent's children dict
                                del item_data["children"][child_id]
                                item_data["children_count"] = len(item_data["children"])

                                message = f"Child item '{child_data['title']}' successfully restored."
                                IStatusMessage(self.request).addStatusMessage(
                                    message, type="info"
                                )
                                self.request.response.redirect(
                                    restored_obj.absolute_url()
                                )
                                return
                        except (KeyError, AttributeError):
                            message = f"Target location not found: {target_path}"
                            IStatusMessage(self.request).addStatusMessage(
                                message, type="error"
                            )
            except Exception as e:
                logger.error(f"Error restoring child item: {e}")
                message = "Failed to restore child item."
                IStatusMessage(self.request).addStatusMessage(message, type="error")

    def get_item(self):
        """Get the specific recycled item"""
        logger.info(f"RecycleBinItemView.get_item called for ID: {self.item_id}")
        if not self.item_id:
            logger.warning("get_item called with no item_id")
            return None

        recycle_bin = getUtility(IRecycleBin)
        item = recycle_bin.get_item(self.item_id)
        if item is None:
            logger.warning(f"No item found in recycle bin with ID: {self.item_id}")
        else:
            logger.info(
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

    def format_date(self, date):
        """Format date for display"""
        return format_date(self.context, date)

    def format_size(self, size_bytes):
        """Format size in bytes to human-readable format"""
        return format_size(size_bytes)


class RecycleBinEnabled(BrowserView):
    """Check if the recycle bin is enabled"""

    def __call__(self):
        """Return True if recycle bin is enabled, else False"""
        recycle_bin = getUtility(IRecycleBin)
        return recycle_bin.is_enabled()
