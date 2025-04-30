from datetime import datetime
from Products.CMFPlone.interfaces.recyclebin import IRecycleBin
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zExceptions import NotFound
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse
from Products.CMFCore.utils import getToolByName
from zope import schema
from z3c.form import button
from z3c.form import field
from z3c.form import form
from plone.z3cform import layout


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
        
        # For comments, add extra information about the content they belong to
        for item in items:
            if item.get('type') == 'Discussion Item':
                # Extract content path from comment path
                path = item.get('path', '')
                # The conversation part is usually ++conversation++default
                parts = path.split('++conversation++')
                if len(parts) > 1:
                    content_path = parts[0]
                    # Remove trailing slash if present
                    if content_path.endswith('/'):
                        content_path = content_path[:-1]
                    item['content_path'] = content_path
                    
                    # Try to get the content title
                    try:
                        content = self.context.unrestrictedTraverse(content_path)
                        item['content_title'] = content.Title()
                    except (KeyError, AttributeError):
                        item['content_title'] = 'Content no longer exists'
        
        return items

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


class IRecycleBinItemForm(Interface):
    """Schema for the recycle bin item form"""
    
    target_container = schema.TextLine(
        title="Target Container",
        description="Path to container where the item should be restored (optional)",
        required=False
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
            self.request.response.redirect(f"{self.context.absolute_url()}/@@recyclebin")
    
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
        if self.item_id is None:  # First traversal
            self.item_id = name
            return self
        raise NotFound(self, name, request)

    def __call__(self):
        """Handle item operations"""
        if self.item_id is None:
            self.request.response.redirect(f"{self.context.absolute_url()}/@@recyclebin")
            return ""
        
        # Initialize and update the form
        form = RecycleBinItemForm(self.context, self.request, self.item_id)
        form.update()
        
        return self.template()

    def get_item(self):
        """Get the specific recycled item"""
        recycle_bin = getUtility(IRecycleBin)
        return recycle_bin.get_item(self.item_id)
    
    def format_date(self, date):
        """Format date for display"""
        if date is None:
            return ""
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        # Use long_format=True to include hours, minutes and seconds
        return portal.restrictedTraverse('@@plone').toLocalizedTime(date, long_format=True)
