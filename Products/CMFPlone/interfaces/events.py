from zope.component.interfaces import IObjectEvent


class ISiteManagerCreatedEvent(IObjectEvent):
    """An event that's fired once the Plone portal is enabled as a site.
    """

class IReorderedEvent(IObjectEvent):
    """An event that's fired once the Plone Tool has been notified of
       a reordering
    """
