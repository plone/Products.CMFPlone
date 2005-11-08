"""Plone Properties tool setup handlers.

$Id:$
"""

from xml.dom.minidom import parseString

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import INodeExporter
from Products.GenericSetup.interfaces import INodeImporter
from Products.GenericSetup.interfaces import PURGE, UPDATE
from Products.GenericSetup.utils import PrettyDocument
from Products.GenericSetup.utils import NodeAdapterBase
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import I18NURI
from Products.CMFPlone.PropertiesTool import SimpleItemWithProperties
from Products.CMFPlone.interfaces import IPropertiesTool, ISimpleItemWithProperties

_FILENAME = 'propertiestool.xml'

def importPloneProperties(context):
    """ Import plone properties tool.
    """
    site = context.getSite()
    mode = context.shouldPurge() and PURGE or UPDATE
    ptool = getToolByName(site, 'portal_properties')

    body = context.readDataFile(_FILENAME)
    if body is None:
        return 'Properties tool: Nothing to import.'

    importer = INodeImporter(ptool, None)
    if importer is None:
        return 'Properties tool: Import adapter misssing.'

    importer.importNode(parseString(body).documentElement, mode=mode)
    return 'Properties tool imported.'

def exportPloneProperties(context):
    """ Export plone properties tool.
    """
    site = context.getSite()

    ptool = getToolByName(site, 'portal_properties', None)
    if ptool is None:
        return 'Properties tool: Nothing to export.'

    exporter = INodeExporter(ptool)
    if exporter is None:
        return 'Properties tool: Export adapter misssing.'

    doc = PrettyDocument()
    doc.appendChild(exporter.exportNode(doc))
    context.writeDataFile(_FILENAME, doc.toprettyxml(' '), 'text/xml')
    return 'Plone properties tool exported.'

class SimpleItemWithPropertiesNodeAdapter(NodeAdapterBase, PropertyManagerHelpers):

    """Node im- and exporter for SimpleItemWithProperties.
    """

    __used_for__ = ISimpleItemWithProperties

    def exportNode(self, doc):
        """Export the object as a DOM node.
        """
        self._doc = doc
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        return node

    def importNode(self, node, mode=PURGE):
        """Import the object from the DOM node.
        """
        self._initProperties(node, mode)


class PlonePropertiesToolNodeAdapter(NodeAdapterBase, ObjectManagerHelpers):

    """Node im- and exporter for Plone PropertiesTool.
    """

    __used_for__ = IPropertiesTool

    def exportNode(self, doc):
        """Export the object as a DOM node.
        """
        self._doc = doc
        node = self._getObjectNode('object')
        node.setAttribute('xmlns:i18n', I18NURI)
        node.appendChild(self._extractObjects())
        return node

    def importNode(self, node, mode=PURGE):
        """Import the object from the DOM node.
        """
        if mode == PURGE:
            self._purgeObjects()

        self._initObjects(node, mode)

    def _initObjects(self, node, mode):
        """Import subobjects"""
        ## XXX: We could just use the _initObjects() from
        ## ObjectManagerHelpers except that it looks up the object
        ## constructor from Products.meta_type and
        ## SimpleItemWithProperties doesn't get registered there.
        for child in node.childNodes:
            if child.nodeName != 'object':
                continue
            if child.hasAttribute('deprecated'):
                continue
            parent = self.context

            obj_id = str(child.getAttribute('name'))
            if obj_id not in parent.objectIds():
                parent._setObject(obj_id, SimpleItemWithProperties(obj_id))
##                 Original _initObjects code:
##                 meta_type = str(child.getAttribute('meta_type'))
##                 for mt_info in Products.meta_types:
##                     if mt_info['name'] == meta_type:
##                         parent._setObject(obj_id, mt_info['instance'](obj_id))
##                         break
##                 else:
##                     raise ValueError('unknown meta_type \'%s\'' % obj_id)

            if child.hasAttribute('insert-before'):
                insert_before = child.getAttribute('insert-before')
                if insert_before == '*':
                    parent.moveObjectsToTop(obj_id)
                else:
                    try:
                        position = parent.getObjectPosition(insert_before)
                        parent.moveObjectToPosition(obj_id, position)
                    except ValueError:
                        pass
            elif child.hasAttribute('insert-after'):
                insert_after = child.getAttribute('insert-after')
                if insert_after == '*':
                    parent.moveObjectsToBottom(obj_id)
                else:
                    try:
                        position = parent.getObjectPosition(insert_after)
                        parent.moveObjectToPosition(obj_id, position+1)
                    except ValueError:
                        pass

            obj = getattr(self.context, obj_id)
            INodeImporter(obj).importNode(child, mode)
