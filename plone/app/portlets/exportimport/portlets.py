from zope.interface import implements
from zope.interface import Interface
from zope.interface import directlyProvides
from zope.interface import providedBy

from zope.component import adapts
from zope.component import getSiteManager
from zope.component import getUtilitiesFor
from zope.component import queryMultiAdapter
from zope.component import getUtility

from zope.component.interfaces import IFactory
from zope.component.interfaces import IComponentRegistry

from zope.app.container.interfaces import INameChooser

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import ISetupEnviron

from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import _getDottedName
from Products.GenericSetup.utils import _resolveDottedName

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager

from plone.app.portlets.interfaces import IPortletTypeInterface
from plone.app.portlets.utils import assignment_mapping_from_key

from plone.app.portlets.exportimport.interfaces import IPortletAssignmentExportImportHandler

from plone.portlets.constants import USER_CATEGORY, GROUP_CATEGORY, CONTENT_TYPE_CATEGORY

from plone.portlets.manager import PortletManager
from plone.portlets.storage import PortletCategoryMapping
from plone.portlets.registration import PortletType

def dummyGetId():
    return ''

class PropertyPortletAssignmentExportImportHandler(object):
    """Import portlet assignment settings based on zope.schema properties
    """
    
    implements(IPortletAssignmentExportImportHandler)
    adapts(Interface)
    
    def __init__(self, assignment):
        self.assignment = assignment
        
    def import_assignment(self, interface, node):
        for child in node.childNodes:
            if child.nodeName != 'property':
                continue
                                    
            property_name = child.getAttribute('name')
            property_value = child.nodeValue
            
            field = getattr(interface, property_name, None)
            if field is None:
                continue
                
            
    
    def export_assignment(interface, fragment):
        # XXX: How do we want this to work?
        pass

class PortletsXMLAdapter(XMLAdapterBase):
    """In- and exporter for a local portlet configuration
    """
    implements(IBody)
    adapts(IComponentRegistry, ISetupEnviron)
    
    name = 'portlets'
    _LOGGER_ID = 'portlets'
    
    def _exportNode(self):
        """Export portlet managers and portlet types
        """
        
        # hack around an issue where _getObjectNode expects to have the context
        # a meta_type and a getId method, which isn't the case for a component
        # registry
        if IComponentRegistry.providedBy(self.context):
            self.context.meta_type = 'ComponentRegistry'
            self.context.getId = dummyGetId
        node = self._getObjectNode('portlets')
        if IComponentRegistry.providedBy(self.context):
            del(self.context.meta_type)
            del(self.context.getId)
        node.appendChild(self._extractPortlets())
        self._logger.info('Portlets exported')
        return node

    def _importNode(self, node):
        """Import portlet managers, portlet types and portlet assignments 
        """
        self._initProvider(node)
        self._logger.info('Portlets imported')

    def _initProvider(self, node):
        if self.environ.shouldPurge():
            self._purgePortlets()
        self._initPortlets(node)

    def _purgePortlets(self):
        """Unregister all portlet managers and portlet types
        """
        
        registeredPortletTypes = [r.name for r in self.context.registeredUtilities()
                                        if r.provided == IPortletType]
                                    
        for name, portletType in getUtilitiesFor(IPortletType):
            if name in registeredPortletTypes:
                self.context.unregisterUtility(provided=IPortletType, name=name)
        
        portletManagerRegistrations = [r for r in self.context.registeredUtilities()
                                        if r.provided.isOrExtends(IPortletManager)]
        
        for registration in portletManagerRegistrations:
            self.context.unregisterUtility(provided=registration.provided,
                                           name=registration.name)
        
        # XXX: Should we purge assignments? What about context assignments?

    def _initPortlets(self, node):
        """Actually import portlet data
        """
        
        site = self.environ.getSite()
        
        registeredPortletTypes = [r.name for r in self.context.registeredUtilities()
                                    if r.provided == IPortletType]
                                        
        registeredPortletManagers = [r.name for r in self.context.registeredUtilities()
                                        if r.provided.isOrExtends(IPortletManager)]
        
        for child in node.childNodes:
            
            # Portlet managers
            if child.nodeName.lower() == 'portletmanager':
                manager = PortletManager()
                name = child.getAttribute('name')
                
                managerType = child.getAttribute('type')
                if managerType:
                    directlyProvides(manager, _resolveDottedName(managerType))
                
                manager[USER_CATEGORY] = PortletCategoryMapping()
                manager[GROUP_CATEGORY] = PortletCategoryMapping()
                manager[CONTENT_TYPE_CATEGORY] = PortletCategoryMapping()
                
                if name not in registeredPortletManagers:
                    self.context.registerUtility(component=manager,
                                                 provided=IPortletManager,
                                                 name=name)
                     
            # Portlet types                            
            elif child.nodeName.lower() == 'portlet':
                addview = child.getAttribute('addview')
                if addview not in registeredPortletTypes:
                    portlet = PortletType()
                    portlet.title = child.getAttribute('title')
                    portlet.description = child.getAttribute('description')
                    portlet.addview = addview
                    
                    for_ = child.getAttribute('for')
                    if for_:
                        portlet.for_ = _resolveDottedName(for_)

                    self.context.registerUtility(component=portlet, 
                                                 provided=IPortletType, 
                                                 name=addview)
                 
            # Portlet assignments                                
            elif child.nodeName.lower() == 'assignment':
                
                # 1. Determine the assignment mapping and the name
                manager = child.getAttribute('manager')
                category = child.getAttribute('category')
                key = child.getAttribute('key')
                type_ = child.getAttribute('type')
                
                mapping = assignment_mapping_from_key(site, manager, category, key)
                
                # 2. Either find or create the assignment
                
                assignment = None
                name = child.getAttribute('name')
                if name:
                    assignment = mapping.get(name, None)
                
                if assignment is None:                    
                    portlet_factory = getUtility(IFactory, name=type_)
                    assignment = portlet_factory()
                    
                    if name is not None:
                        chooser = INameChooser(mapping)
                        name = chooser.chooseName(None, assignment)
                    
                    mapping[name] = assignment

                # 3. Use an adapter to update the portlet settings
                
                portlet_interface = getUtility(IPortletTypeInterface, name=type_)
                assignment_handler = IPortletAssignmentExportImportHandler(assignment)
                assignment_handler.import_assignment(portlet_interface, child)
    
    def _extractPortlets(self):
        """Write portlet managers and types to XML
        """
        fragment = self._doc.createDocumentFragment()
        
        registeredPortletTypes = [r.name for r in self.context.registeredUtilities()
                                            if r.provided == IPortletType]
        portletManagerRegistrations = [r for r in self.context.registeredUtilities()
                                            if r.provided.isOrExtends(IPortletManager)]
        
        for r in portletManagerRegistrations:
            child = self._doc.createElement('portletmanager')
            child.setAttribute('name', r.name)

            specificInterface = providedBy(r.component).flattened().next()
            if specificInterface != IPortletManager:
                child.setAttribute('type', _getDottedName(specificInterface))
            
            fragment.appendChild(child)
            
        for name, portletType in getUtilitiesFor(IPortletType):
            if name in registeredPortletTypes:
                child = self._doc.createElement('portlet')
                child.setAttribute('addview', portletType.addview)
                child.setAttribute('title', portletType.title)
                child.setAttribute('description', portletType.description)
                
                if portletType.for_:
                    child.setAttribute('for', _getDottedName(portletType.for_))

        # XXX: Should we export assignments? Recursively?

        return fragment

def importPortlets(context):
    """Import portlet managers and portlets
    """
    sm = getSiteManager(context.getSite())
    if sm is None or not IComponentRegistry.providedBy(sm):
        logger = context.getLogger('portlets')
        logger.info("Can not register components - no site manager found.")
        return

    # This code was taken from GenericSetup.utils.import.importObjects
    # and slightly simplified. The main difference is the lookup of a named
    # adapter to make it possible to have more than one handler for the same
    # object, which in case of a component registry is crucial.
    importer = queryMultiAdapter((sm, context), IBody, name=u'plone.portlets')
    if importer:
        filename = '%s%s' % (importer.name, importer.suffix)
        body = context.readDataFile(filename)
        if body is not None:
            importer.filename = filename # for error reporting
            importer.body = body

def exportPortlets(context):
    """Export portlet managers and portlets
    """
    sm = getSiteManager(context.getSite())
    if sm is None or not IComponentRegistry.providedBy(sm):
        logger = context.getLogger('portlets')
        logger.info("Nothing to export.")
        return

    # This code was taken from GenericSetup.utils.import.exportObjects
    # and slightly simplified. The main difference is the lookup of a named
    # adapter to make it possible to have more than one handler for the same
    # object, which in case of a component registry is crucial.
    exporter = queryMultiAdapter((sm, context), IBody, name=u'plone.portlets')
    if exporter:
        filename = '%s%s' % (exporter.name, exporter.suffix)
        body = exporter.body
        if body is not None:
            context.writeDataFile(filename, body, exporter.mime_type)

