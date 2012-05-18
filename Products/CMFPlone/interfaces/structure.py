from zope.interface import Interface


class INonStructuralFolder(Interface):
    """Marker for folderish content types that are folderish as an
    implementation detail only.

    By declaring support for this interface, a content type will not be
    considered folderish by the catalog's is_folderish index/metadata, meaning
    that it will not be treated as folderish by the navigation tree, portal tab
    generation and folder_contents.
    """
