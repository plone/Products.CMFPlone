from os.path import dirname

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
        mimetype = "image/vnd.microsoft.icon"
        filename = "favicon.ico"
        if getattr(settings, "site_favicon", False):
            # The user has customized the favicon via the Site configlet.
            filename, data = b64decode_file(settings.site_favicon)
            # Retrieve the MIME type auto-set by the configlet, with a
            # valid fallback to a well-known MIME type.
            mimetype = getattr(settings, "site_favicon_mimetype", mimetype)
        else:
            # No registry favicon, we use our static copy here.
            # Defaults were set above before the if branch.
            fallback_path = os.path.join(dirname(__file__), "static", filename)
            with open(fallback_path, "rb") as icon:
                data = icon.read()
        self.data = NamedImage(data=data, contentType=mimetype, filename=filename)
        self.filename = filename

    def _getFile(self):
        return self.data
