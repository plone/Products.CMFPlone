from Products.CMFPlone.StatelessTreeNav import setupNavTreePropertySheet
from Products.CMFPlone.CustomizationPolicy import DefaultCustomizationPolicy
from Products.CMFCore.utils import getToolByName

def onetwo(portal):
    """ migrates Plone from beta1 to beta2 """
    pcontainer=portal.portal_properties
    # add navtree_properties
    if 'navtree_properties' not in pcontainer.objectIds():
        setupNavTreePropertySheet(pcontainer)

