from zope.interface import Interface


class IHideFromBreadcrumbs(Interface):
    """Marker for content which should not appear in the breadcrumbs.
    """
