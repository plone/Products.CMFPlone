#These CustomizationPolicies *are not* persisted!!
from Products.CMFPlone.Portal import addPolicy
from Products.CMFPlone.interfaces.CustomizationPolicy import ICustomizationPolicy

class DefaultCustomizationPolicy:
    """ Customizes various actions on CMF tools """
    __implements__ = ICustomizationPolicy

    def customize(self, portal):
        # run all the methods in the misc class
        # this will change to use a config file hopefully
        mi_tool = portal.portal_migration
        gs = mi_tool._getWidget('General Setup').__of__(portal)
        gs.addItems(gs.available())

def register(context, app_state):
    addPolicy('Default Plone', DefaultCustomizationPolicy())
