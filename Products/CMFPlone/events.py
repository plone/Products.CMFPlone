from zope.interface import implements
from zope.component.interfaces import ObjectEvent

from interfaces import ISiteManagerCreatedEvent


class SiteManagerCreatedEvent(ObjectEvent):

    implements(ISiteManagerCreatedEvent)
