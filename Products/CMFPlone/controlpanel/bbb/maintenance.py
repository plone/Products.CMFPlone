# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IMaintenanceSchema
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.registry.interfaces import IRegistry
from zope.component import adapts
from zope.component import getUtility
from zope.interface import implements


class MaintenanceControlPanelAdapter(object):

    adapts(IPloneSiteRoot)
    implements(IMaintenanceSchema)

    def __init__(self, context):
        self.context = context
        registry = getUtility(IRegistry)
        self.maintenance_settings = registry.forInterface(
            IMaintenanceSchema, prefix="plone")

    def get_days(self):
        return self.maintenance_settings.days

    def set_days(self, value):
        self.maintenance_settings.days = value

    days = property(get_days, set_days)
