from DateTime import DateTime
from zope.interface import implements
from Products.CMFPlone.interfaces.syndication import ISiteSyndicationSettings
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFCore.PortalFolder import PortalFolderBase
from Products.CMFCore.interfaces import ISyndicationTool
from Products.CMFCore.utils import registerToolInterface


class SyndicationTool(object):
    implements(ISyndicationTool)

    def editProperties(self, updatePeriod=None, updateFrequency=None,
                       updateBase=None, isAllowed=None, max_items=None):
        """
        Edit the properties for the SystemWide defaults on the
        SyndicationTool.
        """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSyndicationSettings)
        if isAllowed is not None:
            settings.enabled = isAllowed

        if updatePeriod is not None:
            settings.update_period = updatePeriod

        if updateFrequency is not None:
            settings.update_frequency = int(updateFrequency)

        if updateBase is not None:
            if type(updateBase) is type(''):
                updateBase = DateTime(updateBase)
            settings.update_base = updateBase.asdatetime()

        if max_items is not None:
            settings.max_items = int(max_items)

    def getSyndicatableContent(self, obj):
        """
        An interface for allowing folderish items to implement an
        equivalent of PortalFolderBase.contentValues()
        """
        if hasattr(obj, 'synContentValues'):
            values = obj.synContentValues()
        else:
            values = PortalFolderBase.contentValues(obj)
        return values

    def isSiteSyndicationAllowed(self):
        """
        Return sitewide syndication policy
        """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSyndicationSettings)
        return settings.enabled

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
        settings = IFeedSettings(obj)
        settings.enabled = True


registerToolInterface('portal_syndication', ISyndicationTool)