from plone.base.interfaces import IReorderedEvent
from plone.base.interfaces import ISiteManagerCreatedEvent
from plone.base.utils import get_installer
from Products.CMFCore.interfaces import IContentish
from plone.base.interfaces.recyclebin import IRecycleBin
from zope.component import adapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface.interfaces import ObjectEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent


@implementer(ISiteManagerCreatedEvent)
class SiteManagerCreatedEvent(ObjectEvent):
    pass


@implementer(IReorderedEvent)
class ReorderedEvent(ObjectEvent):
    pass


def profileImportedEventHandler(event):
    """
    When a profile is imported with the keyword "latest", it needs to
    be reconfigured with the actual number.
    """
    profile_id = event.profile_id
    if profile_id is None:
        return
    profile_id = profile_id.replace("profile-", "")
    gs = event.tool
    installed_version = gs.getLastVersionForProfile(profile_id)
    if installed_version == ("latest",):
        qi = get_installer(gs, gs.REQUEST)
        actual_version = qi.get_latest_upgrade_step(profile_id)
        gs.setLastVersionForProfile(profile_id, actual_version)


def removeBase(event):
    """Make Zope not to inject a <base> tag into the returned HTML
    https://dev.plone.org/ticket/13705
    """
    event.request.response.base = None


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

    # Add to recycle bin - let any exceptions propagate to make problems visible
    recycle_bin.add_item(obj, original_container, original_path)
