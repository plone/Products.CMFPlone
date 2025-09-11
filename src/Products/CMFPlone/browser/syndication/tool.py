from AccessControl import Unauthorized
from Acquisition import aq_parent
from plone.base.interfaces.syndication import IFeed
from plone.base.interfaces.syndication import IFeedSettings
from plone.base.interfaces.syndication import ISiteSyndicationSettings
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import ISyndicationTool
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import registerToolInterface
from zope.component import getAdapter
from zope.component import getUtility
from zope.interface import implementer


@implementer(ISyndicationTool)
class SyndicationTool:
    """
    Backward compatible tool. This just implements
    what some other packages use for now to provide
    backwards compatibility.
    """

    def editProperties(
        self,
        updatePeriod=None,
        updateFrequency=None,
        updateBase=None,
        isAllowed=None,
        max_items=None,
    ):
        """
        Edit the properties for the SystemWide defaults on the
        SyndicationTool.
        """
        registry = getUtility(IRegistry)
        if not _checkPermission(ManagePortal, aq_parent(registry)):
            raise Unauthorized
        settings = registry.forInterface(ISiteSyndicationSettings)
        if isAllowed is not None:
            settings.allowed = isAllowed

        if max_items is not None:
            settings.max_items = int(max_items)

    def getSyndicatableContent(self, obj):
        """
        An interface for allowing folderish items to implement an
        equivalent of PortalFolderBase.contentValues()
        """
        return getAdapter(obj, IFeed)._items()

    def isSiteSyndicationAllowed(self):
        """
        Return sitewide syndication policy
        """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSyndicationSettings)
        return settings.allowed

    def isSyndicationAllowed(self, obj=None):
        """
        Check whether syndication is enabled for the site.  This
        provides for extending the method to check for whether a
        particular obj is enabled, allowing for turning on only
        specific folders for syndication.
        """
        settings = IFeedSettings(obj)
        return settings.enabled

    def enableSyndication(self, obj):
        """
        Enable syndication for the obj
        """
        if not _checkPermission(ModifyPortalContent, obj):
            raise Unauthorized
        settings = IFeedSettings(obj)
        settings.enabled = True

    def disableSyndication(self, obj):
        if not _checkPermission(ModifyPortalContent, obj):
            raise Unauthorized
        settings = IFeedSettings(obj)
        settings.enabled = False


registerToolInterface("portal_syndication", ISyndicationTool)
