from Products.CMFPlone.interfaces import ISiteSchema
from plone.formwidget.namedfile.converter import b64decode_file
from plone.namedfile.browser import Download
from plone.namedfile.file import NamedImage
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from plone.memoize import ram


def render_cachekey(fun, self):
    # Include the name of the viewlet as the underlying cache key only
    # takes the module and function name into account, but not the class
    return "\n".join(
        [
            self.__name__,
            self.filename,
        ]
    )


class SiteFavicon(Download):

    def __init__(self, context, request):
        super().__init__(context, request)
        self.filename = None
        self.data = None

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone")
        if getattr(settings, 'site_favicon', False):
            filename, data = b64decode_file(settings.site_favicon)
            data = NamedImage(data=data, filename=filename)
            self.data = data
            self.filename = filename

    @ram.cache(render_cachekey)
    def _getFile(self):
        return self.data
