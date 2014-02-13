from Products.CMFPlone.interfaces import IFactoryTool
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import exportObjects
from Products.CMFCore.utils import getToolByName


class PortalFactoryXMLAdapter(XMLAdapterBase):
    """In- and exporter for FactoryTool.
    """

    __used_for__ = IFactoryTool

    _LOGGER_ID = name = 'factorytool'

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode("object")
        node.appendChild(self._extractFactoryToolSettings())

        self._logger.info("FactoryTool settings exported.")
        return node

    def _importNode(self, node):
        if self.environ.shouldPurge():
            self._purgeFactoryToolSettings()

        self._initFactoryToolSettings(node)
        self._logger.info("FactoryTool settings imported.")

    def _purgeFactoryToolSettings(self):
        self.context.manage_setPortalFactoryTypes(listOfTypeIds=[])

    def _initFactoryToolSettings(self, node):
        for child in node.childNodes:
            if child.nodeName == "factorytypes":
                types = set(self.context.getFactoryTypes())
                for type in child.getElementsByTagName("type"):
                    types.add(type.getAttribute("portal_type"))
                self.context.manage_setPortalFactoryTypes(
                                    listOfTypeIds=list(types))

    def _extractFactoryToolSettings(self):
        node = self._doc.createElement("factorytypes")
        for t in sorted(self.context.getFactoryTypes()):
            child = self._doc.createElement("type")
            child.setAttribute("portal_type", t)
            node.appendChild(child)

        return node


def importFactoryTool(context):
    """Import Factory Tool configuration.
    """
    site = context.getSite()
    tool = getToolByName(site, 'portal_factory', None)
    if tool is None:
        return

    importObjects(tool, '', context)


def exportFactoryTool(context):
    """Export Factory Tool configuration.
    """
    site = context.getSite()
    tool = getToolByName(site, 'portal_factory', None)
    if tool is None:
        return

    exportObjects(tool, '', context)
