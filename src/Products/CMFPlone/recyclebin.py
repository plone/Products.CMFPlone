from datetime import datetime, timedelta
import logging
import uuid
from persistent.mapping import PersistentMapping
from zope.component import getUtility, getSiteManager
from zope.interface import implementer
from zope.annotation.interfaces import IAnnotations
from plone.registry.interfaces import IRegistry
from zope.component.hooks import getSite

from Products.CMFPlone.interfaces.recyclebin import IRecycleBin
from Products.CMFPlone.controlpanel.browser.recyclerbin import IRecycleBinControlPanelSettings

logger = logging.getLogger("Products.CMFPlone.RecycleBin")

ANNOTATION_KEY = 'Products.CMFPlone.RecycleBin'


@implementer(IRecycleBin)
class RecycleBin(object):
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
        return registry.forInterface(IRecycleBinControlPanelSettings, prefix="plone-recyclebin")
    
    def is_enabled(self):
        """Check if recycle bin is enabled"""
        try:
            settings = self._get_settings()
            return settings.recycling_enabled
        except (KeyError, AttributeError):
            return False
    
    def add_item(self, obj, original_container, original_path):
        """Add deleted item to recycle bin"""
        if not self.is_enabled():
            return None
        
        # Generate a unique ID for the recycled item
        item_id = str(uuid.uuid4())
        
        # Store metadata about the deletion
        self.storage[item_id] = {
            'id': obj.getId(),
            'title': obj.Title(),
            'type': obj.portal_type,
            'path': original_path,
            'parent_path': '/'.join(original_container.getPhysicalPath()),
            'deletion_date': datetime.now(),
            'size': getattr(obj, 'get_size', lambda: 0)(),
            'object': obj,  # Store the actual object
        }
        
        # Check if we need to clean up old items
        self._check_size_limits()
        
        return item_id
    
    def get_items(self):
        """Return all items in recycle bin"""
        items = []
        for item_id, data in self.storage.items():
            item_data = data.copy()
            item_data['recycle_id'] = item_id
            # Don't include the actual object in the listing
            if 'object' in item_data:
                del item_data['object']
            items.append(item_data)
        
        # Sort by deletion date (newest first)
        return sorted(items, key=lambda x: x['deletion_date'], reverse=True)
    
    def get_item(self, item_id):
        """Get a specific deleted item by ID"""
        return self.storage.get(item_id)
    
    def restore_item(self, item_id, target_container=None):
        """Restore item to original location or specified container"""
        if item_id not in self.storage:
            return None
        
        item_data = self.storage[item_id]
        obj = item_data['object']
        obj_id = item_data['id']
        
        # Find the container to restore to
        site = self._get_context()
        if target_container is None:
            # Try to get the original parent
            parent_path = item_data['parent_path']
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
        if obj_id != item_data['id']:
            obj.id = obj_id
        
        # Add object to the target container
        target_container._setObject(obj_id, obj)
        
        # Remove from recycle bin
        del self.storage[item_id]
        
        restored_obj = target_container[obj_id]
        return restored_obj
    
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
            if data['deletion_date'] < cutoff_date:
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
            size = data.get('size', 0)
            total_size += size
            items_by_date.append((item_id, data['deletion_date'], size))
        
        # Sort by date (oldest first)
        items_by_date.sort(key=lambda x: x[1])
        
        # Remove oldest items if size limit is exceeded
        while total_size > max_size_bytes and items_by_date:
            item_id, _, size = items_by_date.pop(0)
            if self.purge_item(item_id):
                total_size -= size
                logger.info(f"Purged item {item_id} due to size constraints")
