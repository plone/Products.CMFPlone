from zope.interface import implements
from zope.interface import Interface

from Products.GenericSetup.interfaces import IFilesystemExporter

# XXX: This is a temporary hack to allow disabling exporting of some
# content types until all of them support proper exporting

class IDisabledExport(Interface):
    pass

class NullExporterAdapter(object):
    """Dummy exporter that does nothing
    """

    implements(IFilesystemExporter)

    def __init__(self, context):
        self.context = context

    def export(self, export_context, subdir):
        pass

    def listExportableItems(self):
        return []
