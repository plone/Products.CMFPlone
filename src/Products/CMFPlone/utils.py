from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from AccessControl import ModuleSecurityInfo
from AccessControl import Unauthorized
from AccessControl.safe_formatter import SafeFormatter
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from App.Common import package_home
from App.Dialogs import MessageDialog
from App.ImageFile import ImageFile
from DateTime import DateTime
from html import escape
from importlib.metadata import distribution
from OFS.CopySupport import CopyError
from os.path import abspath
from os.path import join
from os.path import split
from plone.base import utils as base_utils
from plone.base.interfaces.siteroot import IPloneSiteRoot
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.registry.interfaces import IRegistry
from Products.CMFCore.permissions import ManageUsers
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import ToolInit as CMFCoreToolInit
from Products.CMFPlone import bbb
from Products.CMFPlone.log import log  # noqa: F401 - for python scripts
from Products.CMFPlone.log import log_deprecated  # noqa: F401 - for python scripts
from Products.CMFPlone.log import log_exc  # noqa: F401 - for python scripts
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import providedBy
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.deferredimport import deprecated as deprecated_import
from zope.deprecation import deprecate
from zope.deprecation import deprecated  # noqa: F401
from zope.interface import implementedBy

import OFS
import re
import sys
import zope.interface


# todo: check below if this is still needed
ClassType = type

if bbb.HAS_ZSERVER:
    from webdav.interfaces import IWriteLock
else:
    from OFS.interfaces import IWriteLock

deprecated_import(
    "Import from plone.base.utils instead (will be removed in Plone 7)",
    base_hasattr="plone.base.utils:base_hasattr",
    getEmptyTitle="plone.base.utils:get_empty_title",
    human_readable_size="plone.base.utils:human_readable_size",
    safeToInt="plone.base.utils:safe_int",
    safe_bytes="plone.base.utils:safe_bytes",
    safe_callable="plone.base.utils:safe_callable",
    safe_hasattr="plone.base.utils:safe_hasattr",
    safe_text="plone.base.utils:safe_text",
    get_installer="plone.base.utils:get_installer",
    get_top_request="plone.base.utils:get_top_request",
    get_top_site_from_url="plone.base.utils:get_top_site_from_url",
    pretty_title_or_id="plone.base.utils:pretty_title_or_id",
    _createObjectByType="plone.base.utils:unrestricted_construct_instance",
    transaction_note="plone.base.utils:transaction_note",
    check_id="plone.base.utils:check_id",
    _check_for_collision="plone.base.utils:_check_for_collision",
)

deprecated_import(
    "Import from plone.namedfile.utils instead (will be removed in Plone 7)",
    getHighPixelDensityScales="plone.namedfile.utils:getHighPixelDensityScales",
    getAllowedSizes="plone.namedfile.utils:getAllowedSizes",
    getQuality="plone.namedfile.utils:getQuality",
)


@deprecate("Use plone.base.utils.safe_bytes instead (will be removed in Plone 7)")
def safe_encode(*args, **kwargs):
    return base_utils.safe_bytes(*args, **kwargs)


@deprecate("Use plone.base.utils.safe_text instead (will be removed in Plone 7)")
def safe_unicode(*args, **kwargs):
    return base_utils.safe_text(*args, **kwargs)


@deprecate("Use plone.base.utils.safe_text instead (will be removed in Plone 7)")
def safe_nativestring(value, encoding="utf-8"):
    """Convert a value to str in py2 and to text in py3"""
    if isinstance(value, bytes):
        value = base_utils.safe_text(value, encoding)
    return value


security = ModuleSecurityInfo()
security.declarePrivate("deprecated")
security.declarePrivate("abspath")
security.declarePrivate("re")
security.declarePrivate("OFS")
security.declarePrivate("aq_get")
security.declarePrivate("package_home")
security.declarePrivate("ImageFile")
security.declarePrivate("CMFCoreToolInit")
security.declarePrivate("zope")

# Canonical way to get at CMFPlone directory
PACKAGE_HOME = package_home(globals())
security.declarePrivate("PACKAGE_HOME")
WWW_DIR = join(PACKAGE_HOME, "www")
security.declarePrivate("WWW_DIR")

# image-scaling
QUALITY_DEFAULT = 88
pattern = re.compile(r"^(.*)\s+(\d+)\s*:\s*(\d+)$")

_marker = []


def get_portal():
    """get the Plone portal object.

    It fetched w/o any further context by using the last registered site.
    So this work only after traversal time.
    """
    closest_site = getSite()
    if closest_site is not None:
        for potential_portal in closest_site.aq_chain:
            if IPloneSiteRoot in providedBy(potential_portal):
                return potential_portal


def parent(obj):
    return aq_parent(aq_inner(obj))


def createBreadCrumbs(context, request):
    view = getMultiAdapter((context, request), name="breadcrumbs_view")
    return view.breadcrumbs()


def createSiteMap(context, request, sitemap=False):
    view = getMultiAdapter((context, request), name="sitemap_builder_view")
    return view.siteMap()


def isExpired(content):
    """Find out if the object is expired (copied from skin script)"""

    expiry = None

    # NOTE: We also accept catalog brains as 'content' so that the
    # catalog-based folder_contents will work. It's a little magic, but
    # it works.

    # ExpirationDate should have an ISO date string, which we need to
    # convert to a DateTime

    # Try DC accessor first
    if base_utils.base_hasattr(content, "ExpirationDate"):
        expiry = content.ExpirationDate

    # Try the direct way
    if not expiry and base_utils.base_hasattr(content, "expires"):
        expiry = content.expires

    # See if we have a callable
    if base_utils.safe_callable(expiry):
        expiry = expiry()

    # Convert to DateTime if necessary, ExpirationDate may return 'None'
    if expiry and expiry != "None" and isinstance(expiry, str):
        expiry = DateTime(expiry)

    if isinstance(expiry, DateTime) and expiry.isPast():
        return 1
    return 0


def typesToList(context):
    registry = getUtility(IRegistry)
    return registry.get("plone.displayed_types", ())


def normalizeString(text, context=None, encoding=None):
    # The relaxed mode was removed in Plone 4.0. You should use either the url
    # or file name normalizer from the plone.i18n package instead.
    return queryUtility(IIDNormalizer).normalize(text)


class RealIndexIterator:
    """The 'real' version of the IndexIterator class, that's actually
    used to generate unique indexes.
    """

    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, pos=0):
        self.pos = pos

    def __next__(self):
        # Python 3
        result = self.pos
        self.pos = self.pos + 1
        return result

    next = __next__  # Python 2


@security.private
class ToolInit(CMFCoreToolInit):
    def getProductContext(self, context):
        name = "_ProductContext__prod"
        return getattr(context, name, getattr(context, "__prod", None))

    def getPack(self, context):
        name = "_ProductContext__pack"
        return getattr(context, name, getattr(context, "__pack__", None))

    def getIcon(self, context, path):
        pack = self.getPack(context)
        icon = None
        # This variable is just used for the log message
        icon_path = path
        try:
            icon = ImageFile(path, pack.__dict__)
        except OSError:
            # Fallback:
            # Assume path is relative to CMFPlone directory
            path = abspath(join(PACKAGE_HOME, path))
            try:
                icon = ImageFile(path, pack.__dict__)
            except OSError:
                # if there is some problem loading the fancy image
                # from the tool then  tell someone about it
                log(
                    "The icon for the product: %s which was set to: %s, "
                    "was not found. Using the default." % (self.product_name, icon_path)
                )
        return icon

    def initialize(self, context):
        # Wrap the CMFCore Tool Init method.
        CMFCoreToolInit.initialize(self, context)
        for tool in self.tools:
            # Get the icon path from the tool
            path = getattr(tool, "toolicon", None)
            if path is not None:
                pc = self.getProductContext(context)
                if pc is not None:
                    pid = pc.id
                    name = split(path)[1]
                    icon = self.getIcon(context, path)
                    if icon is None:
                        # Icon was not found
                        return
                    icon.__roles__ = None
                    tool.icon = f"misc_/{self.product_name}/{name}"
                    misc = OFS.misc_.misc_
                    Misc = OFS.misc_.Misc_
                    if not hasattr(misc, pid):
                        setattr(misc, pid, Misc(pid, {}))
                    getattr(misc, pid)[name] = icon


release_levels = ("alpha", "beta", "candidate", "final")
rl_abbr = {"a": "alpha", "b": "beta", "rc": "candidate"}


def versionTupleFromString(v_str):
    """Returns version tuple from passed in version string

    >>> versionTupleFromString('1.2.3')
    (1, 2, 3, 'final', 0)

    >>> versionTupleFromString('2.1-final1 (SVN)')
    (2, 1, 0, 'final', 1)

    >>> versionTupleFromString('3-beta')
    (3, 0, 0, 'beta', 0)

    >>> versionTupleFromString('2.0a3')
    (2, 0, 0, 'alpha', 3)

    >>> versionTupleFromString('foo') is None
    True
    """
    regex_str = (
        r"(^\d+)[.]?(\d*)[.]?(\d*)[- ]?(alpha|beta|candidate|final|a|b|rc)?(\d*)"
    )
    v_regex = re.compile(regex_str)
    match = v_regex.match(v_str)
    if match is None:
        v_tpl = None
    else:
        groups = list(match.groups())
        for i in (0, 1, 2, 4):
            groups[i] = base_utils.safe_int(groups[i])
        if groups[3] is None:
            groups[3] = "final"
        elif groups[3] in rl_abbr.keys():
            groups[3] = rl_abbr[groups[3]]
        v_tpl = tuple(groups)
    return v_tpl


def getFSVersionTuple():
    """Returns Products.CMFPlone version tuple"""
    version = distribution("Products.CMFPlone").version
    return versionTupleFromString(version)


def tuplize(value):
    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    return (value,)


def _detuplize(interfaces, append):
    if isinstance(interfaces, (tuple, list)):
        for sub in interfaces:
            _detuplize(sub, append)
    else:
        append(interfaces)


def flatten(interfaces):
    flattened = []
    _detuplize(interfaces, flattened.append)
    return tuple(flattened)


@deprecate("Use zope.interface.directlyProvides instead (will be removed in Plone 7)")
def directlyProvides(obj, *interfaces):
    return zope.interface.directlyProvides(obj, *interfaces)


@deprecate("Use zope.interface.classImplements instead (will be removed in Plone 7)")
def classImplements(class_, *interfaces):
    return zope.interface.classImplements(class_, *interfaces)


def classDoesNotImplement(class_, *interfaces):
    # convert any Zope 2 interfaces to Zope 3 using fromZ2Interface
    interfaces = flatten(interfaces)
    implemented = implementedBy(class_)
    for iface in interfaces:
        implemented = implemented - iface
    return zope.interface.classImplementsOnly(class_, implemented)


def webdav_enabled(obj, container):
    """WebDAV check used in externalEditorEnabled.py"""

    # Object implements lock interface
    return IWriteLock.providedBy(obj)


# Copied 'unrestricted_rename' from ATCT migrations to avoid
# a dependency.


security.declarePrivate("sys")


def _unrestricted_rename(container, id, new_id):
    """Rename a particular sub-object

    Copied from OFS.CopySupport

    Less strict version of manage_renameObject:
        * no write lock check
        * no verify object check from PortalFolder so it's allowed to rename
          even unallowed portal types inside a folder
    """
    try:
        container._checkId(new_id)
    except Exception:
        raise CopyError(
            MessageDialog(
                title="Invalid Id", message=sys.exc_info()[1], action="manage_main"
            )
        )
    ob = container._getOb(id)
    if not ob.cb_isMoveable():
        raise CopyError(f"Not Supported {escape(id)}")
    try:
        ob._notifyOfCopyTo(container, op=1)
    except Exception:
        raise CopyError(
            MessageDialog(
                title="Rename Error", message=sys.exc_info()[1], action="manage_main"
            )
        )
    container._delObject(id)
    ob = aq_base(ob)
    ob._setId(new_id)

    # Note - because a rename always keeps the same context, we
    # can just leave the ownership info unchanged.
    container._setObject(new_id, ob, set_owner=0)
    ob = container._getOb(new_id)
    ob._postCopy(container, op=1)

    return None


# Copied '_getSecurity' from Archetypes.utils to avoid a dependency.

security.declarePrivate("ClassSecurityInfo")


def _getSecurity(klass, create=True):
    # a Zope 2 class can contain some attribute that is an instance
    # of ClassSecurityInfo. Zope 2 scans through things looking for
    # an attribute that has the name __security_info__ first
    info = vars(klass)
    security = None
    for k, v in info.items():
        if hasattr(v, "__security_info__"):
            security = v
            break
    # Didn't found a ClassSecurityInfo object
    if security is None:
        if not create:
            return None
        # we stuff the name ourselves as __security__, not security, as this
        # could theoretically lead to name clashes, and doesn't matter for
        # zope 2 anyway.
        security = ClassSecurityInfo()
        setattr(klass, "__security__", security)
    return security


def set_own_login_name(member, loginname):
    """Allow the user to set his/her own login name.

    If you have the Manage Users permission, you can update the login
    name of another member too, though the name of this function is a
    bit weird then.  Historical accident.
    """
    portal = getSite()
    pas = getToolByName(portal, "acl_users")
    mt = getToolByName(portal, "portal_membership")
    if member.getId() == mt.getAuthenticatedMember().getId():
        pas.updateOwnLoginName(loginname)
        return
    secman = getSecurityManager()
    if not secman.checkPermission(ManageUsers, member):
        raise Unauthorized("You can only change your OWN login name.")
    pas.updateLoginName(member.getId(), loginname)


def ajax_load_url(url):
    if url and "ajax_load" not in url:
        sep = "?" in url and "&" or "?"  # url parameter separator
        url = f"{url}{sep}ajax_load=1"
    return url


def bodyfinder(text):
    """Return body or unchanged text if no body tags found.

    Always use html_headcheck() first.
    """
    lowertext = text.lower()
    bodystart = lowertext.find("<body")
    if bodystart == -1:
        return text
    bodystart = lowertext.find(">", bodystart) + 1
    if bodystart == 0:
        return text
    bodyend = lowertext.rfind("</body>", bodystart)
    if bodyend == -1:
        return text
    return text[bodystart:bodyend]


def getSiteLogo(site=None, include_type=False):
    from plone.base.interfaces import ISiteSchema
    from plone.formwidget.namedfile.converter import b64decode_file

    import mimetypes

    if site is None:
        site = getSite()
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ISiteSchema, prefix="plone", check=False)
    site_url = site.absolute_url()

    if getattr(settings, "site_logo", False):
        filename, data = b64decode_file(settings.site_logo)
        site_logo_url = f"{site_url}/@@site-logo/{filename}"
        site_logo_type = mimetypes.guess_type(filename)[0]
    else:
        site_logo_url = "%s/++resource++plone-logo.svg" % site_url
        site_logo_type = "image/svg+xml"

    if not include_type:
        return site_logo_url

    return (site_logo_url, site_logo_type)


def _safe_format(inst, method):
    """Use our SafeFormatter that uses guarded_getattr for attribute access.

    This is for use with AccessControl.allow_type,
    as we do in CMFPlone/__init__.py.
    """
    return SafeFormatter(inst).safe_format
