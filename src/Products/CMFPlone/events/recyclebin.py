from Products.CMFCore.interfaces import IContentish
from Products.CMFPlone.interfaces.recyclebin import IRecycleBin
from zope.component import adapter
from zope.component import queryUtility
from zope.lifecycleevent.interfaces import IObjectRemovedEvent


@adapter(IContentish, IObjectRemovedEvent)
def handle_content_removal(obj, event):
    """Event handler for content removal

    This intercepts standard content removal and puts the item in the recycle bin
    instead of letting it be deleted if the recycle bin is enabled.
    """
    # Ignore if the object is being moved
    if getattr(obj, "_v_is_being_moved", False):
        return

    # Get the recycle bin
    recycle_bin = queryUtility(IRecycleBin)
    if recycle_bin is None or not recycle_bin.is_enabled():
        return

    # Only process if this is a direct deletion (not part of container deletion)
    if event.newParent is not None:
        return

    # Get original information
    original_container = event.oldParent
    original_path = "/".join(obj.getPhysicalPath())

    # Add to recycle bin
    try:
        recycle_bin.add_item(obj, original_container, original_path)
    except Exception as e:
        # Log but don't prevent deletion if recycle bin fails
        import logging

        logger = logging.getLogger("Products.CMFPlone.RecycleBin")
        logger.exception(f"Error adding item to recycle bin: {e}")
