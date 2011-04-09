from zope.interface import Interface


class IPortletAssignmentExportImportHandler(Interface):
    """An adapter which is used to export/import GenericSetup configuration
    for a particular portlet assignment type
    """

    def import_assignment(interface, node):
        """Set the properties on the given assignment, based on the given
        portlet type interface. The node is the <assignment /> root node.
        Settings are expected to be found in children of the node.
        """

    def export_assignment(interface, doc, node):
        """Export the properties of the given assignment with the given
        portlet type interface as XML nodes appended to the given node.
        Use the doc object to create new nodes.
        """
