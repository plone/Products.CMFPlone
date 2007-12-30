from zope.interface import implements
from zope.interface import Interface
from zope.interface import directlyProvides
from zope.interface import providedBy

from zope.component import adapts
from zope.component import getSiteManager
from zope.component import getUtilitiesFor
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.component.interfaces import IComponentRegistry

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import ISetupEnviron

from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import _getDottedName
from Products.GenericSetup.utils import _resolveDottedName

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager

from plone.portlets.constants import USER_CATEGORY, GROUP_CATEGORY, CONTENT_TYPE_CATEGORY

from plone.portlets.manager import PortletManager
from plone.portlets.storage import PortletCategoryMapping
from plone.portlets.registration import PortletType

from Products.CMFPlone.utils import log_deprecated

def dummyGetId():
    return ''

class PortletsXMLAdapter(XMLAdapterBase):
    """In- and exporter for a local portlet configuration
    """
    implements(IBody)
    adapts(IComponentRegistry, ISetupEnviron)
    
    name = 'portlets'
    _LOGGER_ID = 'portlets'
    
    def _exportNode(self):
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
        self._initProvider(node)
        self._logger.info('Portlets imported')

    def _initProvider(self, node):
        if self.environ.shouldPurge():
            self._purgePortlets()
        self._initPortlets(node)

    def _purgePortlets(self):
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

    def _initPortlets(self, node):
        registeredPortletManagers = [r.name for r in self.context.registeredUtilities()
                                        if r.provided.isOrExtends(IPortletManager)]
        
        for child in node.childNodes:
            if child.nodeName.lower() == 'portletmanager':
                manager = PortletManager()
                name = str(child.getAttribute('name'))
                
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
                                                 
            elif child.nodeName.lower() == 'portlet':
                self._initPortletNode(child)
    
    def _extractPortlets(self):
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
                fragment.appendChild(self._extractPortletNode(name,
                  portletType))
        
        return fragment
    
    def _extractPortletNode(self, name, portletType):
        child = self._doc.createElement('portlet')
        child.setAttribute('addview', portletType.addview)
        child.setAttribute('title', portletType.title)
        child.setAttribute('description', portletType.description)
        
        for_ = portletType.for_
        #BBB
        for_ = self._BBB_for(for_)
        
        if for_ and for_ != [Interface]:
            for i in for_:
                subNode = self._doc.createElement('for')
                subNode.setAttribute('interface', _getDottedName(i))
                child.appendChild(subNode)
        return child
    
    def _removePortlet(self, name):
        if queryUtility(IPortletType, name=name):
            self.context.unregisterUtility(provided=IPortletType, name=name)
            return True
        else:
            self._logger.warning('Unable to unregister portlet type ' \
              '%s because it is not registered.' % name)
            return False
    
    def _checkBasicPortletNodeErrors(self, node, registeredPortletTypes):
        addview = str(node.getAttribute('addview'))
        extend = node.hasAttribute('extend')
        purge = node.hasAttribute('purge')
        exists = addview in registeredPortletTypes
        
        if extend and purge:
            self._logger.warning('Cannot extend and purge the same ' \
              'portlet type %s!' % addview)
            return True
        if extend and not exists:
            self._logger.warning('Cannot extend portlet type ' \
              '%s because it is not registered.' % addview)
            return True
        if exists and not purge and not extend:
            self._logger.warning('Cannot register portlet type ' \
              '%s because it is already registered.' % addview)
            return True
        
        return False

    def _modifyForList(self, node, for_):
        """Examine the "for_" nodes within a "portlet" node to populate,
        extend, and/or remove interface names from an existing list for_
        """
        modified_for = for_
         
        for subNode in node.childNodes:
            if subNode.nodeName.lower() == 'for':
                interface_name = str(
                  subNode.getAttribute('interface')
                  )
                if subNode.hasAttribute('remove'):
                    if interface_name in modified_for:
                        modified_for.remove(interface_name)
                elif interface_name not in modified_for:
                    modified_for.append(interface_name)
        
        #BBB
        interface_name = str(node.getAttribute('for'))
        if interface_name:
            log_deprecated('The "for" attribute of the portlet node in ' \
            'portlets.xml is deprecated and will be removed in Plone 4.0.' \
            'Use children nodes of the form <for interface="zope.interface.' \
            'Interface" /> instead.')
            modified_for.append(interface_name)
        
        return modified_for
    
    #BBB
    def _BBB_for(self, for_):
        if for_ is None:
            return [Interface]
        if type(for_) not in (tuple, list):
            return [for_]
        return for_
    
    def _initPortletNode(self, node):
        registeredPortletTypes = [
          r.name for r in self.context.registeredUtilities() \
          if r.provided == IPortletType
          ]
        addview = str(node.getAttribute('addview'))
        extend = node.hasAttribute('extend')
        purge = node.hasAttribute('purge')
        
        #In certain cases, continue to the next node
        if node.hasAttribute('remove'):
            self._removePortlet(name=addview)
            return
        if self._checkBasicPortletNodeErrors(node, registeredPortletTypes):
            return

        #To extend a portlet type that is registered, we modify the title and
        #description if provided by the profile, then look up the portlet
        #manager interfaces specified by its for_ attribute
        if extend:
            portlet = queryUtility(IPortletType, name = addview)
            if str(node.getAttribute('title')):
                 portlet.title = str(node.getAttribute('title'))
            if str(node.getAttribute('description')):
                 portlet.description = str(node.getAttribute('description'))
            for_ = portlet.for_
            
            #BBB - to cover old-style for_ attributes that equal None or a
            #single interface
            for_ = self._BBB_for(for_)
            
            for_ = [_getDottedName(i) for i in for_]
        
        #If not extending an already-registered portlet type,
        #then create a new one with the correct attributes.
        if not extend:
             portlet = PortletType()
             portlet.title = str(node.getAttribute('title'))
             portlet.description = str(node.getAttribute('description'))
             portlet.addview = addview
             for_ = []

        #Process the node's child "for" nodes to add or remove portlet
        #manager interface names to the for_ list
        for_ = self._modifyForList(node, for_)
        for_ = [_resolveDottedName(i) for i in for_ \
          if _resolveDottedName(i) is not None]
        
        #Store the for_ attribute, with [Interface] as the default
        if for_ == []:
            for_ = [Interface]
        portlet.for_ = for_
        
        #If "purge" is specified, then remove the old portlet
        #type. We do so immediately before registering the new
        #portlet type to ensure that no errors occur while
        #creating the new portlet type.
        if purge:
            self._removePortlet(addview)
        #If creating a new portlet type, then register it.
        if not extend:
            self.context.registerUtility(component=portlet,
                                         provided=IPortletType,
                                         name=addview)

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
