from zope.interface import implements
from zope.component.interfaces import ObjectEvent

from Products.CMFCore.utils import getToolByName

from interfaces import ISiteManagerCreatedEvent


class SiteManagerCreatedEvent(ObjectEvent):

    implements(ISiteManagerCreatedEvent)


def profileImportedEventHandler(event):
    """
    When a profile is imported with the keyword "latest", it needs to
    be reconfigured with the actual number.
    """
    profile_id = event.profile_id.replace('profile-', '')
    gs = event.tool
    qi = getToolByName(gs, 'portal_quickinstaller')
    installed_version = gs.getLastVersionForProfile(profile_id)
    if installed_version == (u'latest',):
        actual_version = qi.getLatestUpgradeStep(profile_id)
        gs.setLastVersionForProfile(profile_id, actual_version)
