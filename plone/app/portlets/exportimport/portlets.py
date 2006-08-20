from zope.interface import Interface
from zope.interface import directlyProvides

from zope.component import getSiteManager

from zope.publisher.interfaces.browser import IBrowserRequest, IBrowserView

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPlacelessPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer

from plone.z2.portlets.manager import PortletManager, PlacelessPortletManager

from plone.app.portlets.config import PORTLETMANAGER_FOLDER
from plone.app.portlets.interfaces import IPortletManagerFolder

from Acquisition import aq_base
from OFS.Folder import Folder

class PortletsXMLAdapter(XMLAdapterBase):
    """In- and exporter for a local portlet configuration
    """
    __used_for__ = IPortletManagerFolder
    name = 'portlets'
    _LOGGER_ID = 'portlets'
    
    def _exportNode(self):
        node = self._getObjectNode('portlets')
        node.appendChild(self._extractPortletManagers())
        self._logger.info('Portlets exported')
        return node

    def _importNode(self, node):
        self._initProvider(node)
        self._logger.info('Portlets imported')

    def _initProvider(self, node):
        if self.environ.shouldPurge():
            self._purgePortletManagers()
        self._initPortletManagers(node)

    def _purgePortletManagers(self):
        sm = getSiteManager(self.context)
        registrations = [r for r in sm.registeredAdapters()
                            if IPortletManager.providedBy(r.factory)]
        
        for registration in registrations:
            sm.unregisterAdapter(provided=registration.provided,
                                 name=registration.name)

    def _initPortletManagers(self, node):
        sm = getSiteManager(self.context)
        registered = [r.name for r in sm.registeredAdapters()
                        if IPortletManager.providedBy(r.factory)]
        
        
        for child in node.childNodes:
            if child.nodeName != 'portletmanager':
                continue

            id = str(child.getAttribute('id'))
            column = str(child.getAttribute('column'))
            placeless = bool(child.getAttribute('placeless'))
            
            if column in registered:
                continue
            
            if id not in self.context.objectIds():
                if placeless:
                    manager = PortletManager()
                else:
                    manager = PlacelessPortletManager()
                self.context._setObject(id, manager)
            
            manager = self.context._getOb(id)
            
            sm.registerAdapter(required=(Interface, IBrowserRequest, IBrowserView), 
                               provided=IPortletManagerRenderer,
                               name=column, 
                               factory=aq_base(manager))
            

    def _extractPortletManagers(self):
        fragment = self._doc.createDocumentFragment()
    
        sm = getSiteManager(self.context)
        registrations = [r for r in sm.registeredAdapters()
                            if IPortletManager.providedBy(r.factory)]
        
        for r in registrations:
            child = self._doc.createElement('portletmanager')
            child.setAttribute('id', r.factory.getId())
            child.setAttribute('column', r.name)
            if IPlacelessPortletManager.providedBy(r.factory):
                child.setAttribute('placeless', 'True')
            fragment.appendChild(child)

        return fragment

def importPortlets(context):
    """Import portlet managers and portlet assignments
    """

    site = context.getSite()
    
    # Create the container if it does not already exist
    
    if PORTLETMANAGER_FOLDER not in site.objectIds():
        folder = Folder(PORTLETMANAGER_FOLDER)
        site._setObject(PORTLETMANAGER_FOLDER, folder)
        folder = site._getOb(PORTLETMANAGER_FOLDER)
        directlyProvides(folder, IPortletManagerFolder)
    else:
        folder = site._getOb(PORTLETMANAGER_FOLDER)
    
    importObjects(folder, '', context)

def exportPortlets(context):
    """Export portlet managers and portlet assignments
    """
    
    site = context.getSite()
    
    # Create the container if it does not already exist
    
    if PORTLETMANAGER_FOLDER not in site.objectIds():
        folder = PortletManagerFolder(PORTLETMANAGER_FOLDER)
        site._setObject(PORTLETMANAGER_FOLDER, folder)
        folder = site._getOb(PORTLETMANAGER_FOLDER)
    else:
        folder = site._getOb(PORTLETMANAGER_FOLDER)
    
    exportObjects(folder, '', context)
