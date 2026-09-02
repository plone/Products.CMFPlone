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
    root = svgtree.getroot()
    # Every icons.tag() call site renders the icon next to its own text label,
    # so the icons carry no information of their own and are decorative in the
    # ARIA sense. Hide them from assistive technology rather than have screen
    # readers announce them twice.
    root.attrib["aria-hidden"] = "true"
    # The previous "aria-labelledby" pointed at id="title", which was never set
    # on the title element -- and _strip_id removes every id from the tree in
    # any case, so the reference could never resolve. See issue #3394.
    root.attrib.pop("aria-labelledby", None)
    if not cfg.get("title"):
        return
    # Take the namespace from the root element itself rather than from the
    # default namespace mapping: an SVG using a prefixed namespace
    # (<svg:svg xmlns:svg="...">) has no default entry, and nsmap.get(None)
    # would fall back to no namespace at all.
    ns = etree.QName(root).namespace or ""
    # A title tag is still useful: browsers show it as a hover tooltip. It is
    # not used for screen reader labelling, which aria-hidden now suppresses.
    title = root.find(f"{{{ns}}}title")
    if title is None:
        # Build it in the SVG namespace. A bare etree.Element("title") lands in
        # no namespace, so the lookup above could never find a title this code
        # had created and a second pass would append a duplicate one.
        title = etree.SubElement(root, f"{{{ns}}}title" if ns else "title")
    title.text = cfg["title"]


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
        # Calling the @@iconresolver/NAME url directly will lead ZPublisher
        # HTTPResponse add the image/svg+xml mimetype to the response header
        # and encode the body as bytes.
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
            with open(iconfile.path) as fh:
                # Read and return as string.
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
        return etree.tostring(svgtree).decode("utf-8")
