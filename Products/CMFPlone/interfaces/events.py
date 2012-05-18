from zope.component.interfaces import IObjectEvent


class ISiteManagerCreatedEvent(IObjectEvent):
    """An event that's fired once the Plone portal is enabled as a site.
    """
