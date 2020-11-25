# -*- coding: utf-8 -*-
from OFS.Image import File
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from Products.CMFCore.interfaces import ISiteRoot
from zExceptions import NotFound
from zope.component import adapter
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface
from zope.location.interfaces import LocationError
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces import IPublishTraverse
from zExceptions import NotFound

import logging

logger = logging.getLogger(__name__)


@implementer(IPublishTraverse)
class IconsView(BrowserView):

    prefix = "plone.icon."
    defaulticon = "++plone++icons/plone.svg"

    def publishTraverse(self, request, name):
        self.name = name
        return self

    def __call__(self):
        name = getattr(self, "name", None)
        if name is None:
            raise NotFound("No name were given as subpath.")
        fileobj = self._iconfile(self.lookup(self.name))
        return fileobj(REQUEST=self.request, RESPONSE=self.request.response)

    def _iconfile(self, icon):
        site = getSite()
        try:
            return site.restrictedTraverse(icon)
        except NotFound:
            logger.exception(
                f"Icon resolver lookup of '{icon}' failed, fallback to Plone icon."
            )
            return site.restrictedTraverse(self.defaulticon)

    def lookup(self, name):
        __traceback_info__ = name
        registry = getUtility(IRegistry)
        regkey = self.prefix + name
        try:
            return registry[regkey]
        except KeyError:
            if "/" in name:
                main, tail = name.rsplit("/", 1)
                return self.lookup(main)
            logger.exception(
                f"Icon resolver lookup of '{name}' failed, fallback to Plone icon."
            )
            return self.defaulticon

    def url(self, name):
        url = getSite().absolute_url() + "/" + self.lookup(name)
        return url

    def tag(self, name, tag_class="", tag_alt=""):
        icon = self.lookup(name)
        if not icon.endswith(".svg"):
            return f'<img src="{self.url(name)}" class="{tag_class}" alt="{tag_alt}" />'

        iconfile = self._iconfile(icon)
        if isinstance(iconfile, File):
            raise NotImplementedError(
                "Resolve icons stored in database is not yet implemented."
            )
        with open(iconfile.path, "rb") as fh:
            return fh.read()
