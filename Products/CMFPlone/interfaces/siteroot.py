from zope.interface import Interface
from Products.CMFCore.interfaces import ISiteRoot
from plone.app.layout.navigation.interfaces import INavigationRoot


class IPloneSiteRoot(ISiteRoot, INavigationRoot):
    """
    Marker interface for the object which serves as the root of a
    Plone site.
    """


class IMigratingPloneSiteRoot(Interface):
    """
    Marker interface used for migration GenericSetup profiles.
    """


class ITestCasePloneSiteRoot(Interface):
    """
    Marker interface used for test fixture GenericSetup profiles.
    """
