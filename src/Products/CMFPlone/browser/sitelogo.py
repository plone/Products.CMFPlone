from plone.base.interfaces import ISiteSchema
from plone.formwidget.namedfile.converter import b64decode_file
from plone.namedfile.browser import Download
from plone.namedfile.file import NamedImage
from plone.registry.interfaces import IRegistry
from zExceptions import NotFound
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface import noLongerProvides

import hashlib


class IUnversionedSiteLogo(Interface):
    """Marker for a site logo URL without the version of the current logo.

    Its URL stays the same when the logo changes, so it must not be cached
    for long.
    """


def site_logo_version(value):
    """A short hash of the site logo setting, which changes with the logo."""
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()[:16]


class SiteLogo(Download):
    """The site logo from the registry.

    ../@@site-logo/<version>/<filename> can be cached for a long time: a new
    logo gets a new version.  ../@@site-logo/<filename> and URLs with an old
    version still show the current logo, but get a different caching ruleset
    (see caching.zcml), so they are revalidated.
    """

    def __init__(self, context, request):
        super().__init__(context, request)
        self.filename = None
        self.data = None
        self.version = None
        self.traversed = []

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone")
        if getattr(settings, "site_logo", False):
            filename, data = b64decode_file(settings.site_logo)
            data = NamedImage(data=data, filename=filename)
            self.data = data
            self.filename = filename
            self.version = site_logo_version(settings.site_logo)
            # self.width, self.height = self.data.getImageSize()
        alsoProvides(self, IUnversionedSiteLogo)

    def publishTraverse(self, request, name):
        # ../@@site-logo/<filename> or ../@@site-logo/<version>/<filename>
        if len(self.traversed) >= 2:
            raise NotFound(self, name, request)
        self.traversed.append(name)
        if len(self.traversed) == 2 and self.is_current_version(self.traversed[0]):
            # Use the caching ruleset of SiteLogo, not of the marker.
            noLongerProvides(self, IUnversionedSiteLogo)
        return self

    def is_current_version(self, version):
        return self.version is not None and version == self.version

    def __call__(self):
        if self.data is None:
            raise NotFound(self, "site-logo", self.request)
        return super().__call__()

    def get_canonical(self, file):
        from Products.CMFPlone.utils import getSiteLogo

        return getSiteLogo()

    def _getFile(self):
        return self.data
