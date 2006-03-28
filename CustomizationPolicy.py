#These CustomizationPolicies *are not* persisted!!
from Products.CMFPlone.Portal import addPolicy
from Products.CMFPlone.interfaces.CustomizationPolicy \
     import ICustomizationPolicy as z2ICustomizationPolicy
from Products.CMFPlone.interfaces import ICustomizationPolicy

from zope.interface import implements

class DefaultCustomizationPolicy:
    """ Customizes various actions on CMF tools """
    __implements__ = z2ICustomizationPolicy

    implements(ICustomizationPolicy)

    availableAtConstruction=1

    def customize(self, portal):
        # run all the methods in the misc class
        # this will change to use a config file hopefully
        mi_tool = portal.portal_migration
        gs = mi_tool._getWidget('General Setup')
        gs.addItems(gs.available())


def register(context, app_state):
    addPolicy('Default Plone', DefaultCustomizationPolicy())
