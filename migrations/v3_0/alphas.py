from zope.app.component.interfaces import ISite
from zope.component.globalregistry import base
from zope.component.persistentregistry import PersistentComponents

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.migrations.migration_util import installOrReinstallProduct
from Products.Five.component import enableSite
from Products.Five.component.interfaces import IObjectManagerSite

def three0_alpha1(portal):
    """2.5.x -> 3.0-alpha1
    """
    out = []

    # Make the portal a Zope3 site
    enableZope3Site(portal, out)

    # Add new css files to RR
    addNewCSSFiles(portal, out)

    # Install CMFEditions and 
    installProduct('CMFEditions', portal, out)
    installProduct('CMFDiffTool', portal, out)

    return out


def enableZope3Site(portal, out):
    if not ISite.providedBy(portal):
        enableSite(portal, iface=IObjectManagerSite)

        components = PersistentComponents()
        components.__bases__ = (base,)
        portal.setSiteManager(components)

        out.append('Made the portal a Zope3 site.')


def addNewCSSFiles(portal, out):
    # add new css files to the portal_css registries
    cssreg = getToolByName(portal, 'portal_css', None)
    stylesheet_ids = cssreg.getResourceIds()
    if 'navtree.css' not in stylesheet_ids:
        cssreg.registerStylesheet('navtree.css', media='screen')
        cssreg.moveResourceAfter('navtree.css', 'textLarge.css')
        out.append("Added navtree.css to the registry")
    if 'invisibles.css' not in stylesheet_ids:
        cssreg.registerStylesheet('invisibles.css', media='screen')
        cssreg.moveResourceAfter('invisibles.css', 'navtree.css')
        out.append("Added invisibles.css to the registry")
    if 'forms.css' not in stylesheet_ids:
        cssreg.registerStylesheet('forms.css', media='screen')
        cssreg.moveResourceAfter('forms.css', 'invisibles.css')
        out.append("Added forms.css to the registry")


def installProduct(product, portal, out):
    """Quickinstalls a product if it is not installed yet."""
    if product in portal.Control_Panel.Products.objectIds():
        installOrReinstallProduct(portal, product, out)
