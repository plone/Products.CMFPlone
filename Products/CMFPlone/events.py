from plone.base.interfaces import IReorderedEvent
from plone.base.interfaces import ISiteManagerCreatedEvent
from plone.base.utils import get_installer
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface.interfaces import ObjectEvent


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


def set_ajax(event):
    """Set the ajax_load parameter automatically for AJAX requests."""

    registry = queryUtility(IRegistry)
    if registry is None:
        return

    if not registry.get("plone.ajax_marker"):
        # Autmatic ajax_load request marking disabled.
        return

    request = event.request

    # If ajax_load was already set to a true-ish or false-ish value, don't set
    # it again.
    if (
        request.getHeader("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"
        and "ajax_load" not in request
    ):
        # Directly set on the request object
        request.set("ajax_load", True)
