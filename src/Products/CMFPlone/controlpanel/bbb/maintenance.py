from plone.base.interfaces import IMaintenanceSchema
from plone.base.interfaces import IPloneSiteRoot
from plone.registry.interfaces import IRegistry
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer

import warnings


@adapter(IPloneSiteRoot)
@implementer(IMaintenanceSchema)
class MaintenanceControlPanelAdapter:
    def __init__(self, context):
        warnings.warn(
            f"Usage of bbb controlpanel '{self.__class__.__name__}' is deprecated. "
            "Use registry.forInterface(plone.base.interfaces.IMaintenanceSchema, prefix='plone') instead. "
            "It will be removed in Plone 7.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.context = context
        registry = getUtility(IRegistry)
        self.maintenance_settings = registry.forInterface(
            IMaintenanceSchema, prefix="plone"
        )

    def get_days(self):
        return self.maintenance_settings.days

    def set_days(self, value):
        self.maintenance_settings.days = value

    days = property(get_days, set_days)
