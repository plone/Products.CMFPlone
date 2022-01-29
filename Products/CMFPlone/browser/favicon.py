import os

from Products.CMFPlone.interfaces import ISiteSchema
from plone.formwidget.namedfile.converter import b64decode_file
from plone.memoize import ram
from plone.namedfile.browser import Download
from plone.namedfile.file import NamedImage
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class SiteFavicon(Download):

    def __init__(self, context, request):
        super().__init__(context, request)
        self.filename = None
        self.data = None

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone")
        if getattr(settings, 'site_favicon', False):
            filename, data = b64decode_file(settings.site_favicon)
            mimetype = getattr(settings, 'site_favicon_mimetype', "image/vnd.microsoft.icon")
            data = NamedImage(data=data, contentType=mimetype, filename=filename)
            self.data = data
            self.filename = filename
        else:
            basedir = os.path.dirname(os.path.dirname(__file__))
            with open(os.path.join(basedir, "skins", "plone_images", "default-favicon.ico"), "rb") as icon:
                data = NamedImage(data=icon.read(), contentType="image/vnd.microsoft.icon", filename="favicon.ico")
            self.data = data
            self.filename = "favicon.ico"

    def _getFile(self):
        return self.data
