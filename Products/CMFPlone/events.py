from zExceptions import NotFound
from ZPublisher.interfaces import IPubAfterTraversal

from zope.interface import implements
from zope.component.interfaces import ObjectEvent
from zope.component import adapter

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IContentish

from interfaces import ISiteManagerCreatedEvent
from interfaces import IReorderedEvent


class SiteManagerCreatedEvent(ObjectEvent):

    implements(ISiteManagerCreatedEvent)


class ReorderedEvent(ObjectEvent):
    implements(IReorderedEvent)


def profileImportedEventHandler(event):
    """
    When a profile is imported with the keyword "latest", it needs to
    be reconfigured with the actual number.
    """
    profile_id = event.profile_id
    if profile_id is None:
        return
    profile_id = profile_id.replace('profile-', '')
    gs = event.tool
    qi = getToolByName(gs, 'portal_quickinstaller', None)
    if qi is None:
        # CMF-only site, or a test run.
        return
    installed_version = gs.getLastVersionForProfile(profile_id)
    if installed_version == (u'latest',):
        actual_version = qi.getLatestUpgradeStep(profile_id)
        gs.setLastVersionForProfile(profile_id, actual_version)


@adapter(IPubAfterTraversal)
def avoid_acquired_content(event):
    request = event.request
    parents = request['PARENTS']
    context = parents[0]
    if IContentish.providedBy(context):
        parent_ids = [item.getId() for item in parents]
        parent_ids.reverse()
        acquired = parent_ids != list(context.getPhysicalPath())
        if acquired:
            raise NotFound(request.URL)
