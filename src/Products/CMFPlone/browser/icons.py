from lxml import etree
from OFS.Image import File
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from zExceptions import NotFound
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import logging


logger = logging.getLogger(__name__)


SVG_MODIFER = {}


def _add_aria_title(svgtree, cfg):
    if not cfg.get("title"):
        return
    root = svgtree.getroot()
    ns = root.nsmap.get(None, "")
    # set title tag
    title = root.find(f"{{{ns}}}title")
    if title is None:
        title = etree.Element("title")
        root.append(title)
    title.text = cfg["title"]
    # add aria attr
    root.attrib["aria-labelledby"] = "title"


SVG_MODIFER["add_aria_title"] = _add_aria_title

ADDITIONAL_CLASSES = [
    # this classes are added to all svg root elements
    "plone-icon",
]


def _add_css_class(svgtree, cfg):
    root = svgtree.getroot()
    current = root.attrib.get("class", "")
    root.attrib["class"] = f"{' '.join(ADDITIONAL_CLASSES)} {cfg['cssclass']} {current}"


SVG_MODIFER["add_css_class"] = _add_css_class


def _strip_id(svgtree, cfg):
    for el in svgtree.getroot().xpath("//*[@id]"):
        del el.attrib["id"]


SVG_MODIFER["strip_id"] = _strip_id


@implementer(IPublishTraverse)
class IconsView(BrowserView):
    prefix = "plone.icon."
    defaulticon = "++plone++icons/plone.svg"
    name = ""

    def publishTraverse(self, request, name):
        if self.name:
            # fix traversing to eg. "contenttype/document"
            self.name += "/"
        self.name += name
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
            logger.info(
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
        try:
            with open(iconfile.path, "rb") as fh:
                svgtree = etree.parse(fh)
        except etree.XMLSyntaxError:
            logger.exception(f"SVG File: {iconfile.path}")
            with open(iconfile.path, "rb") as fh:
                return fh.read()
        if svgtree.docinfo.root_name.lower() != "svg":
            raise ValueError(
                f"SVG file content root tag mismatch (not svg but {svgtree.docinfo.root_name}): {iconfile.path}"
            )
        modifier_cfg = {
            "cssclass": tag_class,
            "title": tag_alt,
        }
        for name, modifier in SVG_MODIFER.items():
            __traceback_info__ = name
            modifier(svgtree, modifier_cfg)
        return etree.tostring(svgtree)
