from datetime import datetime
from Products.CMFPlone.interfaces.recyclebin import IRecycleBin
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zExceptions import NotFound
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from Products.CMFCore.utils import getToolByName


class RecycleBinView(BrowserView):
    """Browser view for recycle bin management"""

    template = ViewPageTemplateFile("templates/recyclebin.pt")

    def __call__(self):
        form = self.request.form

        if form.get("form.submitted", False):
            if form.get("form.button.Restore", None) is not None:
                self.restore_items()
            elif form.get("form.button.Delete", None) is not None:
                self.delete_items()
            elif form.get("form.button.Empty", None) is not None:
                self.empty_bin()

        return self.template()

    def get_recycle_bin(self):
        """Get the recycle bin utility"""
        return getUtility(IRecycleBin)

    def get_items(self):
        """Get all items in the recycle bin"""
        recycle_bin = self.get_recycle_bin()
        return recycle_bin.get_items()

    def format_date(self, date):
        """Format date for display"""
        if date is None:
            return ""
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        # Use long_format=True to include hours, minutes and seconds
        return portal.restrictedTraverse('@@plone').toLocalizedTime(date, long_format=True)

    def format_size(self, size_bytes):
        """Format size in bytes to human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def restore_items(self):
        """Restore selected items from the recycle bin"""
        form = self.request.form
        recycle_bin = self.get_recycle_bin()

        # Get the selected items
        selected_items = form.get("selected_items", [])
        if not isinstance(selected_items, list):
            selected_items = [selected_items]

        if not selected_items:
            message = "No items selected for restoration."
            IStatusMessage(self.request).addStatusMessage(message, type="info")
            return

        restored_count = 0
        for item_id in selected_items:
            if recycle_bin.restore_item(item_id):
                restored_count += 1

        message = f"{restored_count} item{'s' if deleted_count != 1} restored successfully."
        IStatusMessage(self.request).addStatusMessage(message, type="info")

    def delete_items(self):
        """Permanently delete selected items"""
        form = self.request.form
        recycle_bin = self.get_recycle_bin()

        # Get the selected items
        selected_items = form.get("selected_items", [])
        if not isinstance(selected_items, list):
            selected_items = [selected_items]

        if not selected_items:
            message = "No items selected for deletion."
            IStatusMessage(self.request).addStatusMessage(message, type="info")
            return

        deleted_count = 0
        for item_id in selected_items:
            if recycle_bin.purge_item(item_id):
                deleted_count += 1

        message = f"{deleted_count} item{'s' if deleted_count != 1} permanently deleted."
        IStatusMessage(self.request).addStatusMessage(message, type="info")

    def empty_bin(self):
        """Empty the entire recycle bin"""
        recycle_bin = self.get_recycle_bin()
        items = recycle_bin.get_items()
        deleted_count = 0

        for item in items:
            item_id = item["recycle_id"]
            if recycle_bin.purge_item(item_id):
                deleted_count += 1

        message = f"Recycle bin emptied. {deleted_count} item{'s' if deleted_count != 1} permanently deleted."
        IStatusMessage(self.request).addStatusMessage(message, type="info")


@implementer(IPublishTraverse)
class RecycleBinItemView(BrowserView):
    """View for managing individual recycled items"""

    template = ViewPageTemplateFile("templates/recyclebin_item.pt")
    item_id = None

    def publishTraverse(self, request, name):
        """Handle URLs like /recyclebin/item/[item_id]"""
        if self.item_id is None:  # First traversal
            self.item_id = name
            return self
        raise NotFound(self, name, request)

    def __call__(self):
        """Handle item operations"""
        if self.item_id is None:
            self.request.response.redirect(f"{self.context.absolute_url()}/recyclebin")
            return ""

        form = self.request.form
        if form.get("form.submitted", False):
            if form.get("form.button.Restore", None) is not None:
                self.restore_item()
                return ""
            elif form.get("form.button.Delete", None) is not None:
                self.delete_item()
                return ""

        return self.template()

    def get_item(self):
        """Get the specific recycled item"""
        recycle_bin = getUtility(IRecycleBin)
        return recycle_bin.get_item(self.item_id)

    def restore_item(self):
        """Restore this item"""
        recycle_bin = getUtility(IRecycleBin)

        # Get target container if specified
        target_path = self.request.form.get("target_container", "")
        target_container = None

        if target_path:
            try:
                target_container = self.context.unrestrictedTraverse(target_path)
            except (KeyError, AttributeError):
                message = f"Target location not found: {target_path}"
                IStatusMessage(self.request).addStatusMessage(message, type="error")
                self.request.response.redirect(
                    f"{self.context.absolute_url()}/recyclebin/item/{self.item_id}"
                )
                return

        # Restore the item
        restored_obj = recycle_bin.restore_item(self.item_id, target_container)

        if restored_obj:
            message = f"Item '{restored_obj.Title()}' successfully restored."
            IStatusMessage(self.request).addStatusMessage(message, type="info")
            self.request.response.redirect(restored_obj.absolute_url())
        else:
            message = (
                "Failed to restore item. It may have been already restored or deleted."
            )
            IStatusMessage(self.request).addStatusMessage(message, type="error")
            self.request.response.redirect(f"{self.context.absolute_url()}/recyclebin")

    def delete_item(self):
        """Permanently delete this item"""
        recycle_bin = getUtility(IRecycleBin)

        # Get item info before deletion
        item = self.get_item()
        if item:
            item_title = item.get("title", "Unknown")

            if recycle_bin.purge_item(self.item_id):
                message = f"Item '{item_title}' permanently deleted."
                IStatusMessage(self.request).addStatusMessage(message, type="info")
            else:
                message = f"Failed to delete item '{item_title}'."
                IStatusMessage(self.request).addStatusMessage(message, type="error")
        else:
            message = "Item not found. It may have been already deleted."
            IStatusMessage(self.request).addStatusMessage(message, type="error")

        self.request.response.redirect(f"{self.context.absolute_url()}/recyclebin")
