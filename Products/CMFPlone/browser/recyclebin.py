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


class IRecycleBinForm(Interface):
    """Schema for the Recycle Bin form"""

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

    @button.buttonAndHandler("Delete Selected", name="delete")
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
        print(f"Child items to exclude: {child_items_to_exclude}")

        # Only include items that are not children of other recycled items
        items = [item for item in items if item.get("id") not in child_items_to_exclude]
        print(f"Filtered items: {items}")

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

        return items

    def format_date(self, date):
        """Format date for display"""
        if date is None:
            return ""
        portal = getToolByName(self.context, "portal_url").getPortalObject()
        # Use long_format=True to include hours, minutes and seconds
        return portal.restrictedTraverse("@@plone").toLocalizedTime(
            date, long_format=True
        )

    def format_size(self, size_bytes):
        """Format size in bytes to human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"


class IRecycleBinItemForm(Interface):
    """Schema for the recycle bin item form"""

    target_container = schema.TextLine(
        title="Target Container",
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

    @button.buttonAndHandler("Restore Item", name="restore")
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

    @button.buttonAndHandler("Permanently Delete", name="delete")
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
                                    item_data["children_count"] = len(
                                        item_data["children"]
                                    )

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

        # Initialize and update the form
        form = RecycleBinItemForm(self.context, self.request, self.item_id)
        form.update()

        # Get the item before rendering template
        item = self.get_item()
        if item is None:
            logger.warning(
                f"No item found with ID: {self.item_id}, redirecting to main recyclebin view"
            )
            self.request.response.redirect(
                f"{self.context.absolute_url()}/@@recyclebin"
            )
            return ""

        logger.info(f"Found item with title: {item.get('title', 'Unknown')}")
        return self.template()

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
        """Get the children of this item if it's a folder/collection"""
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
        if date is None:
            return ""
        portal = getToolByName(self.context, "portal_url").getPortalObject()
        # Use long_format=True to include hours, minutes and seconds
        return portal.restrictedTraverse("@@plone").toLocalizedTime(
            date, long_format=True
        )

    def format_size(self, size_bytes):
        """Format size in bytes to human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"


class RecycleBinEnabled(BrowserView):
    """Check if the recycle bin is enabled"""

    def __call__(self):
        """Return True if recycle bin is enabled, else False"""
        recycle_bin = getUtility(IRecycleBin)
        return recycle_bin.is_enabled()
