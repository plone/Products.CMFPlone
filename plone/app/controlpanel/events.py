from zope.component import adapter
from zope.component import queryUtility
from zope.interface import implements
from zope.ramcache.interfaces.ram import IRAMCache

from plone.app.controlpanel.interfaces import IConfigurationChangedEvent

class ConfigurationChangedEvent(object):
    implements(IConfigurationChangedEvent)

    def __init__(self, context, data):
        self.context = context
        self.data = data


@adapter(IConfigurationChangedEvent)
def handleConfigurationChangedEvent(event):
    util = queryUtility(IRAMCache)
    if util is not None:
        util.invalidateAll()
