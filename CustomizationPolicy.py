#These CustomizationPolicies *are not* persisted!!
from Products.CMFPlone.Portal import addPolicy
from Products.CMFPlone.interfaces.CustomizationPolicy import ICustomizationPolicy
from Products.CMFPlone import Configuration

class DefaultCustomizationPolicy:
    """ Customizes various actions on CMF tools """
    __implements__ = ICustomizationPolicy
        
    def customize(self, portal):
        configklass=Configuration.getCurrentConfiguration()
        config=configklass()
        for meth in config._methods:
            method=getattr(config, meth)
            method(portal)

def register(context, app_state):
    addPolicy('Default Plone', DefaultCustomizationPolicy())

