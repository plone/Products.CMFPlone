from zope.interface import Interface


class IRecycleBin(Interface):
    """Interface for the recycle bin functionality"""
    
    def add_item(obj, original_container, original_path):
        """Add deleted item to recycle bin
        
        Args:
            obj: The object being deleted
            original_container: The parent container before deletion
            original_path: The full path to the object before deletion
        
        Returns:
            The ID of the item in the recycle bin
        """
    
    def get_items():
        """Return all items in recycle bin
        
        Returns:
            A list of dictionaries with information about deleted items
        """
    
    def get_item(item_id):
        """Get a specific deleted item by ID
        
        Args:
            item_id: The ID of the deleted item in the recycle bin
            
        Returns:
            Dictionary with item information or None if not found
        """
    
    def restore_item(item_id, target_container=None):
        """Restore item to original location or specified container
        
        Args:
            item_id: The ID of the item in the recycle bin
            target_container: Optional target container to restore to
                              (defaults to original container)
        
        Returns:
            The restored object or None if restore failed
        """
    
    def purge_item(item_id):
        """Permanently delete an item
        
        Args:
            item_id: The ID of the item in the recycle bin
            
        Returns:
            Boolean indicating success
        """
    
    def purge_expired_items():
        """Purge items that exceed the retention period
        
        Returns:
            Number of items purged
        """
