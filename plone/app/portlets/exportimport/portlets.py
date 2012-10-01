"""
When creating custom portlet managers, you will need to extend
existing portlets to be addable to that manager: ::

    <portlet extend="True" addview="portlets.Calendar">
      <for interface="my.package.interfaces.ICustomPortletManager"/>
    </portlet>

You can also change the title and description of the portlet with the
extend attribute: ::

    <portlet
      extend="True"
      title="Dates of inquisition"
      description="Nobody expects the SpanishInquisition!"
      addview="portlets.Calendar"/>

Remove a portlet definition using the 'remove' attribute so that it can
no longer be added via @@manage-portlets. This does not remove
any assignments: ::

    <portlet remove="True" addview="portlets.Calendar"/>

.. These docs are used in c.developermanual
.. original content from http://www.sixfeetup.com/company/technologies/plone-content-management-new/quick-reference-cards/swag/swag-images-files/generic_setup.pdf


"""

from operator import attrgetter

from zope.interface import implements
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.interface import providedBy

from zope.component import adapts
from zope.component import getSiteManager
from zope.component import getUtilitiesFor
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.component import getUtility

from zope.component.interfaces import IFactory
from zope.component.interfaces import IComponentRegistry

from zope.schema.interfaces import IField
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import IFromUnicode

from zope.container.interfaces import INameChooser

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import ISetupEnviron

from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import _getDottedName
from Products.GenericSetup.utils import _resolveDottedName

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletAssignmentSettings

from plone.app.portlets.interfaces import IDefaultPortletManager
from plone.app.portlets.interfaces import IPortletTypeInterface
from plone.app.portlets.utils import assignment_mapping_from_key

from plone.app.portlets.exportimport.interfaces import IPortletAssignmentExportImportHandler

from plone.portlets.constants import USER_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import CONTENT_TYPE_CATEGORY
from plone.portlets.constants import CONTEXT_CATEGORY

from plone.portlets.manager import PortletManager
from plone.portlets.storage import PortletCategoryMapping
from plone.portlets.registration import PortletType



def dummyGetId():
    return ''


HAS_BLACKLIST = True
try:
    from Products.GenericSetup.interfaces import IComponentsHandlerBlacklist
except ImportError:
    HAS_BLACKLIST = False

if HAS_BLACKLIST:

    class Blacklist(object):
        implements(IComponentsHandlerBlacklist)

        def getExcludedInterfaces(self):
            return (_getDottedName(IPortletType),
                    _getDottedName(IPortletManager),
                    _getDottedName(IPortletManagerRenderer),
                    )


class PropertyPortletAssignmentExportImportHandler(object):
    """Import portlet assignment settings based on zope.schema properties
    """

    implements(IPortletAssignmentExportImportHandler)
    adapts(Interface)

    def __init__(self, assignment):
        self.assignment = assignment

    def import_assignment(self, interface, node):
        for child in node.childNodes:
            if child.nodeName == 'property':
                self.import_node(interface, child)

    def export_assignment(self, interface, doc, node):
        for field_name in interface:
            field = interface[field_name]

            if not IField.providedBy(field):
                continue

            child = self.export_field(doc, field)
            node.appendChild(child)

    # Helper methods

    def import_node(self, interface, child):
        """Import a single <property /> node
        """
        property_name = child.getAttribute('name')

        field = interface.get(property_name, None)
        if field is None:
            return

        field = field.bind(self.assignment)
        value = None

        # If we have a collection, we need to look at the value_type.
        # We look for <element>value</element> child nodes and get the
        # value from there
        if ICollection.providedBy(field):
            value_type = field.value_type
            value = []
            for element in child.childNodes:
                if element.nodeName != 'element':
                    continue
                element_value = self.extract_text(element)
                value.append(self.from_unicode(value_type, element_value))
            value = self.field_typecast(field, value)

        # Otherwise, just get the value of the <property /> node
        else:
            value = self.extract_text(child)
            if not (field.getName() == 'root' and value in ['', '/']):
                value = self.from_unicode(field, value)

        if field.getName() == 'root' and value in ['', '/']:
            # these valid values don't pass validation of SearchableTextSourceBinder
            field.set(self.assignment, value)
        else:
            field.validate(value)
            field.set(self.assignment, value)

    def export_field(self, doc, field):
        """Turn a zope.schema field into a node and return it
        """
        field = field.bind(self.assignment)
        value = field.get(self.assignment)

        child = doc.createElement('property')
        child.setAttribute('name', field.__name__)

        if value is not None:
            if ICollection.providedBy(field):
                for e in value:
                    list_element = doc.createElement('element')
                    list_element.appendChild(doc.createTextNode(str(e)))
                    child.appendChild(list_element)
            else:
                child.appendChild(doc.createTextNode(unicode(value)))

        return child

    def extract_text(self, node):
        node.normalize()
        text = u""
        for child in node.childNodes:
            if child.nodeType == node.TEXT_NODE or child.nodeType == node.CDATA_SECTION_NODE:
                text += child.nodeValue
        return text

    def from_unicode(self, field, value):

        # XXX: Bool incorrectly omits to declare that it implements
        # IFromUnicode, even though it does.
        import zope.schema
        if IFromUnicode.providedBy(field) or isinstance(field, zope.schema.Bool):
            return field.fromUnicode(value)
        else:
            return self.field_typecast(field, value)

    def field_typecast(self, field, value):
        # A slight hack to force sequence types to the right type
        typecast = getattr(field, '_type', None)
        if typecast is not None:
            if not isinstance(typecast, (list, tuple)):
                typecast = (typecast, )
            for tc in reversed(typecast):
                if callable(tc):
                    try:
                        value = tc(value)
                        break
                    except:
                        pass
        return value


class PortletsXMLAdapter(XMLAdapterBase):
    """In- and exporter for a local portlet configuration
    """
    implements(IBody)
    adapts(IComponentRegistry, ISetupEnviron)

    name = 'portlets'
    _LOGGER_ID = 'portlets'

    #
    # Main control flow
    #

    def _exportNode(self):
        """Export portlet managers and portlet types
        """
        node = self._doc.createElement('portlets')
        node.appendChild(self._extractPortlets())
        self._logger.info('Portlets exported')
        return node

    def _importNode(self, node):
        """Import portlet managers, portlet types and portlet assignments
        """
        self._initProvider(node)
        self._logger.info('Portlets imported')

    def _initProvider(self, node):
        purge = self.environ.shouldPurge()
        if node.hasAttribute('purge'):
            purge = self._convertToBoolean(node.getAttribute('purge'))
        if purge:
            self._purgePortlets()
        self._initPortlets(node)

    #
    # Purge
    #

    def _purgePortlets(self):
        """Unregister all portlet managers and portlet types, and remove
        portlets assigned to the site root
        """

        # Purge portlet types

        registeredPortletTypes = [r.name for r in self.context.registeredUtilities()
                                        if r.provided == IPortletType]

        for name, portletType in getUtilitiesFor(IPortletType):
            if name in registeredPortletTypes:
                self.context.unregisterUtility(provided=IPortletType, name=name)

        # Purge portlets assigned to the site root
        site = self.environ.getSite()

        for name, portletManager in getUtilitiesFor(IPortletManager):
            assignable = queryMultiAdapter((site, portletManager), IPortletAssignmentMapping)
            if assignable is not None:
                for key in list(assignable.keys()):
                    del assignable[key]

        # Purge portlet manager registrations - this will also get rid of
        # global portlet registrations, since these utilities disappear

        portletManagerRegistrations = [r for r in self.context.registeredUtilities()
                                        if r.provided.isOrExtends(IPortletManager)]

        for registration in portletManagerRegistrations:
            self.context.unregisterUtility(provided=registration.provided,
                                           name=registration.name)

    #
    # Importing
    #

    def _initPortlets(self, node):
        """Actually import portlet data
        """
        for child in node.childNodes:
            # Portlet managers
            if child.nodeName.lower() == 'portletmanager':
                self._initPortletManagerNode(child)
            elif child.nodeName.lower() == 'portlet':
                self._initPortletNode(child)
            # Portlet assignments
            elif child.nodeName.lower() == 'assignment':
                self._initAssignmentNode(child)
            # Blacklisting (portlet blocking/unblocking)
            elif child.nodeName.lower() == 'blacklist':
                self._initBlacklistNode(child)

    def _initPortletManagerNode(self, node):
        """Create a portlet manager from a node
        """
        name = str(node.getAttribute('name'))

        if node.hasAttribute('remove'):
            if self._convertToBoolean(node.getAttribute('remove')):
                self.context.unregisterUtility(provided=IPortletManager,
                                               name=name)
                return

        if node.hasAttribute('purge'):
            if self._convertToBoolean(node.getAttribute('purge')):
                manager = getUtility(IPortletManager, name=name)
                # remove global assignments
                for category in manager.keys():
                    for portlet in manager[category].keys():
                        del manager[category][portlet]
                # remove assignments from root
                site = self.environ.getSite()
                mapping = queryMultiAdapter((site, manager), IPortletAssignmentMapping)
                for portlet in mapping.keys():
                    del mapping[portlet]
                return

        registeredPortletManagers = [r.name for r in self.context.registeredUtilities()
                                        if r.provided.isOrExtends(IPortletManager)]
        if name not in registeredPortletManagers:
            managerClass = node.getAttribute('class')
            if managerClass:
                manager = _resolveDottedName(managerClass)()
            else:
                manager = PortletManager()

            managerType = node.getAttribute('type')
            if managerType:
                alsoProvides(manager, _resolveDottedName(managerType))

            manager[USER_CATEGORY] = PortletCategoryMapping()
            manager[GROUP_CATEGORY] = PortletCategoryMapping()
            manager[CONTENT_TYPE_CATEGORY] = PortletCategoryMapping()

            self.context.registerUtility(component=manager,
                                         provided=IPortletManager,
                                         name=name)

    def _initPortletNode(self, node):
        """Create a portlet type from a node
        """
        registeredPortletTypes = [
          r.name for r in self.context.registeredUtilities() \
                          if r.provided == IPortletType]

        addview = str(node.getAttribute('addview'))
        extend = node.hasAttribute('extend')
        purge = node.hasAttribute('purge')

        #In certain cases, continue to the next node
        if node.hasAttribute('remove'):
            self._removePortlet(name=addview)
            return
        if self._checkBasicPortletNodeErrors(node, registeredPortletTypes):
            return

        #Retrieve or create the portlet type and determine the current list
        #of associated portlet manager interfaces (for_)
        if extend:
            #To extend a portlet type that is registered, we modify the title
            #and description if provided by the profile.
            portlet = queryUtility(IPortletType, name = addview)
            if str(node.getAttribute('title')):
                portlet.title = str(node.getAttribute('title'))
            if str(node.getAttribute('description')):
                portlet.description = str(node.getAttribute('description'))
            for_ = portlet.for_
            if for_ is None:
                for_ = []
        else:
            #Otherwise, create a new portlet type with the correct attributes.
            portlet = PortletType()
            portlet.title = str(node.getAttribute('title'))
            portlet.description = str(node.getAttribute('description'))
            portlet.addview = addview
            for_ = []


        #Process the node's child "for" nodes to add or remove portlet
        #manager interface names to the for_ list
        for_ = self._modifyForList(node, for_)

        #Store the for_ attribute, with [IDefaultPortletManager] as the default
        if for_ == []:
            for_ = [IDefaultPortletManager]
        portlet.for_ = for_

        if purge:
            self._removePortlet(addview)
        if not extend:
            self.context.registerUtility(component=portlet,
                                         provided=IPortletType,
                                         name=addview)

    def _initAssignmentNode(self, node):
        """Create an assignment from a node
        """
        site = self.environ.getSite()

        # 1. Determine the assignment mapping and the name
        manager = node.getAttribute('manager')
        category = node.getAttribute('category')
        key = node.getAttribute('key')
        # convert unicode to str as unicode paths are not allowed in
        # restrictedTraverse called in assignment_mapping_from_key
        key = key.encode()

        purge = False
        if node.hasAttribute('purge'):
            purge = self._convertToBoolean(node.getAttribute('purge'))

        mapping = assignment_mapping_from_key(site, manager, category, key, create=True)

        # 2. Either find or create the assignment

        assignment = None
        name = node.getAttribute('name')
        if name:
            assignment = mapping.get(name, None)

        if node.hasAttribute('remove'):
            if assignment is not None:
                del mapping[name]
            return

        if purge:
            for portlet in mapping.keys():
                del mapping[portlet]
            return

        type_ = node.getAttribute('type')

        if assignment is None:
            portlet_factory = getUtility(IFactory, name=type_)
            assignment = portlet_factory()

            if not name:
                chooser = INameChooser(mapping)
                name = chooser.chooseName(None, assignment)

            mapping[name] = assignment

        # aq-wrap it so that complex fields will work
        assignment = assignment.__of__(site)

        # set visibility setting
        visible = node.getAttribute('visible')
        if visible:
            settings = IPortletAssignmentSettings(assignment)
            settings['visible'] = self._convertToBoolean(visible)

        # 3. Use an adapter to update the portlet settings

        portlet_interface = getUtility(IPortletTypeInterface, name=type_)
        assignment_handler = IPortletAssignmentExportImportHandler(assignment)
        assignment_handler.import_assignment(portlet_interface, node)

        # 4. Handle ordering

        insert_before = node.getAttribute('insert-before')
        if insert_before:
            position = None
            keys = list(mapping.keys())

            if insert_before == "*":
                position = 0
            elif insert_before in keys:
                position = keys.index(insert_before)

            if position is not None:
                keys.remove(name)
                keys.insert(position, name)
                mapping.updateOrder(keys)

    def _initBlacklistNode(self, node):
        """Create a blacklisting from a node
        """
        site = self.environ.getSite()

        manager = node.getAttribute('manager')
        category = node.getAttribute('category')
        location = str(node.getAttribute('location'))
        status = node.getAttribute('status')

        manager = getUtility(IPortletManager, name=manager)

        if location.startswith('/'):
            location = location[1:]

        item = site.unrestrictedTraverse(location, None)
        if item is None:
            return

        assignable = queryMultiAdapter((item, manager), ILocalPortletAssignmentManager)

        if status.lower() == 'block':
            assignable.setBlacklistStatus(category, True)
        elif status.lower() == 'show':
            assignable.setBlacklistStatus(category, False)
        elif status.lower() == 'acquire':
            assignable.setBlacklistStatus(category, None)


    #
    # Exporting
    #

    def _extractPortlets(self):
        """Write portlet managers and types to XML
        """
        fragment = self._doc.createDocumentFragment()
        site = self.environ.getSite()

        registeredPortletTypes = [r.name for r in self.context.registeredUtilities()
                                            if r.provided == IPortletType]
        portletManagerRegistrations = [r for r in self.context.registeredUtilities()
                                            if r.provided.isOrExtends(IPortletManager)]

        portletSchemata = dict([(iface, name) for name, iface in getUtilitiesFor(IPortletTypeInterface)])

        # Export portlet manager registrations

        for r in sorted(portletManagerRegistrations, key=attrgetter('name')):
            fragment.appendChild(self._extractPortletManagerNode(r))

        # Export portlet type registrations

        for name, portletType in getUtilitiesFor(IPortletType):
            if name in sorted(registeredPortletTypes):
                fragment.appendChild(self._extractPortletNode(name, portletType))

        def extractMapping(manager_name, category, key, mapping):
            for name, assignment in mapping.items():
                type_ = None
                for schema in providedBy(assignment).flattened():
                    type_ = portletSchemata.get(schema, None)
                    if type_ is not None:
                        break

                if type_ is not None:
                    child = self._doc.createElement('assignment')
                    child.setAttribute('manager', manager_name)
                    child.setAttribute('category', category)
                    child.setAttribute('key', key)
                    child.setAttribute('type', type_)
                    child.setAttribute('name', name)

                    assignment = assignment.__of__(mapping)

                    settings = IPortletAssignmentSettings(assignment)
                    visible = settings.get('visible', True)
                    child.setAttribute('visible', repr(visible))

                    handler = IPortletAssignmentExportImportHandler(assignment)
                    handler.export_assignment(schema, self._doc, child)
                    fragment.appendChild(child)

        # Export assignments in the global categories
        for category in (USER_CATEGORY, GROUP_CATEGORY, CONTENT_TYPE_CATEGORY):
            for manager_name, manager in getUtilitiesFor(IPortletManager):
                for key, mapping in manager.get(category, {}).items():
                    mapping = mapping.__of__(site)
                    extractMapping(manager_name, category, key, mapping)


        # Export assignments at the root of the portal (only)
        for manager_name, manager in getUtilitiesFor(IPortletManager):
            mapping = queryMultiAdapter((site, manager), IPortletAssignmentMapping)
            mapping = mapping.__of__(site)
            extractMapping(manager_name, CONTEXT_CATEGORY, u"/", mapping)

        # Export blacklistings in the portal root
        for manager_name, manager in getUtilitiesFor(IPortletManager):
            assignable = queryMultiAdapter((site, manager), ILocalPortletAssignmentManager)
            if assignable is None:
                continue
            for category in (USER_CATEGORY, GROUP_CATEGORY, CONTENT_TYPE_CATEGORY, CONTEXT_CATEGORY):
                child = self._doc.createElement('blacklist')
                child.setAttribute('manager', manager_name)
                child.setAttribute('category', category)
                child.setAttribute('location', u"/")

                status = assignable.getBlacklistStatus(category)
                if status == True:
                    child.setAttribute('status', u'block')
                elif status == False:
                    child.setAttribute('status', u'show')
                else:
                    child.setAttribute('status', u'acquire')

                fragment.appendChild(child)

        return fragment

    def _extractPortletManagerNode(self, portletManagerRegistration):
        r = portletManagerRegistration
        child = self._doc.createElement('portletmanager')
        if r.component.__class__ is not PortletManager:
            child.setAttribute('class', _getDottedName(r.component.__class__))
        child.setAttribute('name', r.name)

        specificInterface = providedBy(r.component).flattened().next()
        if specificInterface != IPortletManager:
            child.setAttribute('type', _getDottedName(specificInterface))

        return child

    def _extractPortletNode(self, name, portletType):
        child = self._doc.createElement('portlet')
        child.setAttribute('addview', portletType.addview)
        child.setAttribute('title', portletType.title)
        child.setAttribute('description', portletType.description)

        for_ = portletType.for_
        #BBB

        # [Interface] is previous default value
        if for_ and for_ not in ([IDefaultPortletManager], [Interface]):
            for i in for_:
                subNode = self._doc.createElement('for')
                subNode.setAttribute('interface', _getDottedName(i))
                child.appendChild(subNode)
        return child

    #
    # Helper methods
    #

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

    def _removePortlet(self, name):
        if queryUtility(IPortletType, name=name):
            self.context.unregisterUtility(provided=IPortletType, name=name)
            return True
        else:
            self._logger.warning('Unable to unregister portlet type ' \
              '%s because it is not registered.' % name)
            return False

    def _modifyForList(self, node, for_):
        """Examine the "for_" nodes within a "portlet" node to populate,
        extend, and/or remove interface names from an existing list for_
        """
        modified_for = [_getDottedName(i) for i in for_]

        for subNode in node.childNodes:
            if subNode.nodeName.lower() == 'for':
                interface_name = str(subNode.getAttribute('interface'))
                if subNode.hasAttribute('remove'):
                    if interface_name in modified_for:
                        modified_for.remove(interface_name)
                elif interface_name not in modified_for:
                    modified_for.append(interface_name)

        if node.hasAttribute("for"):
            raise InvalidPortletForDefinition(node)

        modified_for = [_resolveDottedName(name) for name in modified_for \
          if _resolveDottedName(name) is not None]

        return modified_for


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


class InvalidPortletForDefinition(Exception):

    message = """The following portlet definition is invalid: %s
The 'for' attribute is not supported, use 'for' sub-elements instead.
See http://plone.org/documentation/manual/upgrade-guide/version/\
upgrading-plone-3-x-to-4.0/updating-add-on-products-for-plone-4.0/\
portlets-generic-setup-syntax-changes for more information.
"""

    def __init__(self, node):
        node = node.toxml()
        self.args = [self.message % node, ]
