from zope.interface import Interface


class IPloneBaseTool(Interface):
    """Marker interface for plone tools
    """


class IPloneTool(Interface):
    """Marker interface for the plone utils tool.
    """


class IPloneCatalogTool(Interface):
    """Marker interface for Plone's catalog tool
    """
