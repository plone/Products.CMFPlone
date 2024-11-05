from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from AccessControl.class_init import InitializeClass
from Acquisition import aq_base
from ComputedAttribute import ComputedAttribute
from five.localsitemanager.registry import PersistentComponents
from OFS.ObjectManager import REPLACEABLE
from plone.base.interfaces.siteroot import IPloneSiteRoot
from plone.base.interfaces.syndication import ISyndicatable
from plone.base.permissions import AddPortalContent
from plone.base.permissions import AddPortalFolders
from plone.base.permissions import ListPortalMembers
from plone.base.permissions import ModifyPortalContent
from plone.base.permissions import ReplyToItem
from plone.base.permissions import View
from plone.dexterity.content import Container
from Products.CMFCore import permissions
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.permissions import AddPortalMember
from Products.CMFCore.permissions import MailForgottenPassword
from Products.CMFCore.permissions import RequestReview
from Products.CMFCore.permissions import ReviewPortalContent
from Products.CMFCore.permissions import SetOwnPassword
from Products.CMFCore.permissions import SetOwnProperties
from Products.CMFCore.PortalFolder import PortalFolderBase
from Products.CMFCore.PortalObject import PortalObjectBase
from Products.CMFCore.Skinnable import SkinnableObjectManager
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject
from Products.CMFPlone import bbb
from Products.Five.component.interfaces import IObjectManagerSite
from zope.event import notify
from zope.interface import classImplementsOnly
from zope.interface import implementedBy
from zope.interface import implementer
from zope.interface.interfaces import ComponentLookupError
from zope.traversing.interfaces import BeforeTraverseEvent


if bbb.HAS_ZSERVER:
    from webdav.NullResource import NullResource


@implementer(IPloneSiteRoot, ISiteRoot, ISyndicatable, IObjectManagerSite)
class PloneSite(Container, SkinnableObjectManager, UniqueObject):
    """The Plone site object."""

    security = ClassSecurityInfo()
    meta_type = portal_type = "Plone Site"

    # Ensure certain attributes come from the correct base class.
    _checkId = SkinnableObjectManager._checkId
    manage_main = PortalFolderBase.manage_main

    def __getattr__(self, name):
        try:
            # Try DX
            return super().__getattr__(name)
        except AttributeError:
            # Check portal_skins
            return SkinnableObjectManager.__getattr__(self, name)

    def __setattr__(self, name, obj):
        # handle re setting an item as an attribute
        if not name.startswith("_") and self._tree is not None and name in self:
            del self[name]
            self[name] = obj
        else:
            super().__setattr__(name, obj)

    def __delattr__(self, name):
        try:
            return super().__delattr__(name)
        except AttributeError:
            return self.__delitem__(name)

    # Removes the 'Components Folder'

    manage_options = Container.manage_options[:2] + Container.manage_options[3:]

    __ac_permissions__ = (
        (AccessContentsInformation, ()),
        (AddPortalMember, ()),
        (SetOwnPassword, ()),
        (SetOwnProperties, ()),
        (MailForgottenPassword, ()),
        (RequestReview, ()),
        (ReviewPortalContent, ()),
        (AddPortalContent, ()),
        (AddPortalFolders, ()),
        (ListPortalMembers, ()),
        (ReplyToItem, ()),
        (View, ("isEffective",)),
        (
            ModifyPortalContent,
            (
                "manage_cutObjects",
                "manage_pasteObjects",
                "manage_renameForm",
                "manage_renameObject",
                "manage_renameObjects",
            ),
        ),
    )

    # Switch off ZMI ordering interface as it assumes a slightly
    # different functionality
    has_order_support = 0
    management_page_charset = "utf-8"
    _default_sort_key = "id"
    _properties = (
        {"id": "title", "type": "string", "mode": "w"},
        {"id": "description", "type": "text", "mode": "w"},
    )
    title = ""
    description = ""
    icon = "misc_/CMFPlone/tool.gif"

    # From PortalObjectBase
    def __init__(self, id, title=""):
        super().__init__(id, title=title)
        components = PersistentComponents("++etc++site")
        components.__parent__ = self
        self.setSiteManager(components)

    # From PortalObjectBase
    def __before_publishing_traverse__(self, arg1, arg2=None):
        """Pre-traversal hook."""
        # XXX hack around a bug(?) in BeforeTraverse.MultiHook
        REQUEST = arg2 or arg1

        try:
            notify(BeforeTraverseEvent(self, REQUEST))
        except ComponentLookupError:
            # allow ZMI access, even if the portal's site manager is missing
            pass
        self.setupCurrentSkin(REQUEST)

        super().__before_publishing_traverse__(arg1, arg2)

    # Concept from OFS.OrderSupport
    @security.protected(permissions.AccessContentsInformation)
    def tpValues(self):
        # Return a list of subobjects, used by ZMI tree tag (and only there).
        # see also https://github.com/plone/Products.CMFPlone/issues/3323
        return sorted(
            (
                obj
                for obj in self.objectValues()
                if getattr(aq_base(obj), "isPrincipiaFolderish", False)
            ),
            key=lambda obj: obj.getId(),
        )

    def __browser_default__(self, request):
        """Set default so we can return whatever we want instead
        of index_html"""
        return getToolByName(self, "plone_utils").browserDefault(self)

    def index_html(self):
        """Acquire if not present."""
        request = getattr(self, "REQUEST", None)
        if (
            request is not None
            and "REQUEST_METHOD" in request
            and request.maybe_webdav_client
        ):
            method = request["REQUEST_METHOD"]
            if bbb.HAS_ZSERVER and method in ("PUT",):
                # Very likely a WebDAV client trying to create something
                result = NullResource(self, "index_html")
                setattr(result, "__replaceable__", REPLACEABLE)
                return result
            elif method not in ("GET", "HEAD", "POST"):
                raise AttributeError("index_html")
        # Acquire from skin.
        _target = self.__getattr__("index_html")
        result = aq_base(_target).__of__(self)
        setattr(result, "__replaceable__", REPLACEABLE)
        return result

    index_html = ComputedAttribute(index_html, 1)

    def manage_beforeDelete(self, container, item):
        # Should send out an Event before Site is being deleted.
        self.removal_inprogress = 1
        PloneSite.inheritedAttribute("manage_beforeDelete")(self, container, item)

    @security.protected(permissions.DeleteObjects)
    def manage_delObjects(self, ids=None, REQUEST=None):
        """We need to enforce security."""
        if ids is None:
            ids = []
        if isinstance(ids, str):
            ids = [ids]
        for id in ids:
            item = self._getOb(id)
            if not _checkPermission(permissions.DeleteObjects, item):
                raise Unauthorized("Do not have permissions to remove this object")
        return PortalObjectBase.manage_delObjects(self, ids, REQUEST=REQUEST)

    def view(self):
        """Ensure that we get a plain view of the object, via a delegation to
        __call__(), which is defined in BrowserDefaultMixin
        """
        return self()

    @security.protected(permissions.AccessContentsInformation)
    def folderlistingFolderContents(self, contentFilter=None):
        """Calls listFolderContents in protected only by ACI so that
        folder_listing can work without the List folder contents permission.

        This is copied from Archetypes Basefolder and is needed by the
        reference browser.
        """
        return self.listFolderContents(contentFilter)

    def isEffective(self, date):
        # Override DefaultDublinCoreImpl's test, since we are always viewable.
        return 1


# Remove the IContentish interface so we don't listen to events that won't
# apply to the site root, ie handleUidAnnotationEvent
classImplementsOnly(PloneSite, implementedBy(PloneSite) - IContentish)

InitializeClass(PloneSite)
