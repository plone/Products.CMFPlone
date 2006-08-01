from zope.app.component.interfaces import ISite
from zope.component.globalregistry import base
from zope.component.persistentregistry import PersistentComponents

from Products.Five.component import enableSite
from Products.Five.component.interfaces import IObjectManagerSite

def three0_alpha1(portal):
    """2.5.x -> 3.0-alpha1
    """
    out = []

    # Make the portal a Zope3 site
    enableZope3Site(portal, out)

    return out

def enableZope3Site(portal, out):
    if not ISite.providedBy(portal):
        enableSite(portal, iface=IObjectManagerSite)

        components = PersistentComponents()
        components.__bases__ = (base,)
        portal.setSiteManager(components)

        out.append('Made the portal a Zope3 site.')
