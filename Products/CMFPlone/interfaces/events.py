from zope.component.interfaces import IObjectEvent
from zope.interface import Attribute
from zope.interface import Interface


class ISiteManagerCreatedEvent(IObjectEvent):
    """An event that's fired once the Plone portal is enabled as a site.
    """

class IReorderedEvent(IObjectEvent):
    """An event that's fired once the Plone Tool has been notified of
       a reordering
    """


class IConfigurationChangedEvent(Interface):
    """An event which is fired after a configuration setting has been changed.
    """

    context = Attribute("The configuration context which was changed.")

    data = Attribute("The configuration data which was changed.")
