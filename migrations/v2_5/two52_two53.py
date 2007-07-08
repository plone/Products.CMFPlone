from Products.CMFCore.utils import getToolByName


def two52_two53(portal):
    """2.5.2 -> 2.5.3
    """
    out = []
    addMissingMimeTypes(portal, out)

    return out


def addMissingMimeTypes(portal, out):
    """ add mime types that weren't included with the MimetypesRegistry that
        shipped with Plone 2.5.2 and are now required (#6695)
    """
    # manage_addMimeType handles existing types gracefully, so we can just go
    # ahead and add them without testing for existing ones
    portal.mimetypes_registry.manage_addMimeType('text/x-web-markdown', \
        ['text/x-web-markdown'], ['markdown'], 'text.png')
    portal.mimetypes_registry.manage_addMimeType('text/x-web-textile', \
        ['text/x-web-textile'], ['textile'], 'text.png')
    out.append("Added `text/x-web-markdown` and `text/x-web-textile`.")
