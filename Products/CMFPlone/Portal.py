from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from AccessControl.class_init import InitializeClass
from Acquisition import aq_base
from ComputedAttribute import ComputedAttribute
from five.localsitemanager.registry import PersistentComponents
from OFS.ObjectManager import REPLACEABLE
from plone.dexterity.content import Container
from plone.i18n.locales.interfaces import IMetadataLanguageAvailability
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
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.interfaces.syndication import ISyndicatable
from Products.CMFPlone.permissions import AddPortalContent
from Products.CMFPlone.permissions import AddPortalFolders
from Products.CMFPlone.permissions import ListPortalMembers
from Products.CMFPlone.permissions import ModifyPortalContent
from Products.CMFPlone.permissions import ReplyToItem
from Products.CMFPlone.permissions import View
from Products.Five.component.interfaces import IObjectManagerSite
from zope.component import queryUtility
from zope.component.interfaces import ComponentLookupError
from zope.event import notify
from zope.interface import classImplementsOnly
from zope.interface import implementedBy
from zope.interface import implementer
from zope.traversing.interfaces import BeforeTraverseEvent


if bbb.HAS_ZSERVER:
    from webdav.NullResource import NullResource


@implementer(IPloneSiteRoot, ISiteRoot, ISyndicatable, IObjectManagerSite)
class PloneSite(Container, SkinnableObjectManager, UniqueObject):
    """ The Plone site object. """

    security = ClassSecurityInfo()
    meta_type = portal_type = 'Plone Site'

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
        if self._tree is not None and name in self:
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

    manage_options = (
        Container.manage_options[:2] +
        Container.manage_options[3:])

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
        (View, ('isEffective',)),
        (ModifyPortalContent, ('manage_cutObjects', 'manage_pasteObjects',
                               'manage_renameForm', 'manage_renameObject',
                               'manage_renameObjects')))

    # Switch off ZMI ordering interface as it assumes a slightly
    # different functionality
    has_order_support = 0
    management_page_charset = 'utf-8'
    _default_sort_key = 'id'
    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w'},
        {'id': 'description', 'type': 'text', 'mode': 'w'},
    )
    title = ''
    description = ''
    icon = 'misc_/CMFPlone/tool.gif'

    # From PortalObjectBase
    def __init__(self, id, title=''):
        super(PloneSite, self).__init__(id, title=title)
        components = PersistentComponents('++etc++site')
        components.__parent__ = self
        self.setSiteManager(components)

    # From PortalObjectBase
    def __before_publishing_traverse__(self, arg1, arg2=None):
        """ Pre-traversal hook.
        """
        # XXX hack around a bug(?) in BeforeTraverse.MultiHook
        REQUEST = arg2 or arg1

        try:
            notify(BeforeTraverseEvent(self, REQUEST))
        except ComponentLookupError:
            # allow ZMI access, even if the portal's site manager is missing
            pass
        self.setupCurrentSkin(REQUEST)

        super(PloneSite, self).__before_publishing_traverse__(arg1, arg2)

    def __browser_default__(self, request):
        """ Set default so we can return whatever we want instead
        of index_html """
        return getToolByName(self, 'plone_utils').browserDefault(self)

    def index_html(self):
        """ Acquire if not present. """
        request = getattr(self, 'REQUEST', None)
        if (
            request is not None
            and 'REQUEST_METHOD' in request
            and request.maybe_webdav_client
        ):
            method = request['REQUEST_METHOD']
            if bbb.HAS_ZSERVER and method in ('PUT', ):
                # Very likely a WebDAV client trying to create something
                result = NullResource(self, 'index_html')
                setattr(result, '__replaceable__', REPLACEABLE)
                return result
            elif method not in ('GET', 'HEAD', 'POST'):
                raise AttributeError('index_html')
        # Acquire from skin.
        _target = self.__getattr__('index_html')
        result = aq_base(_target).__of__(self)
        setattr(result, '__replaceable__', REPLACEABLE)
        return result

    index_html = ComputedAttribute(index_html, 1)

    def manage_beforeDelete(self, container, item):
        # Should send out an Event before Site is being deleted.
        self.removal_inprogress = 1
        PloneSite.inheritedAttribute('manage_beforeDelete')(self, container,
                                                            item)

    security.declareProtected(permissions.DeleteObjects, 'manage_delObjects')

    def manage_delObjects(self, ids=None, REQUEST=None):
        """We need to enforce security."""
        if ids is None:
            ids = []
        if isinstance(ids, str):
            ids = [ids]
        for id in ids:
            item = self._getOb(id)
            if not _checkPermission(permissions.DeleteObjects, item):
                raise Unauthorized(
                    "Do not have permissions to remove this object")
        return PortalObjectBase.manage_delObjects(self, ids, REQUEST=REQUEST)

    def view(self):
        """ Ensure that we get a plain view of the object, via a delegation to
        __call__(), which is defined in BrowserDefaultMixin
        """
        return self()

    security.declareProtected(permissions.AccessContentsInformation,
                              'folderlistingFolderContents')

    def folderlistingFolderContents(self, contentFilter=None):
        """Calls listFolderContents in protected only by ACI so that
        folder_listing can work without the List folder contents permission.

        This is copied from Archetypes Basefolder and is needed by the
        reference browser.
        """
        return self.listFolderContents(contentFilter)

    security.declarePublic('availableLanguages')

    def availableLanguages(self):
        util = queryUtility(IMetadataLanguageAvailability)
        languages = util.getLanguageListing()
        languages.sort(lambda x, y: cmp(x[1], y[1]))
        # Put language neutral at the top.
        languages.insert(0, ('', _('Language neutral (site default)')))

        return languages

    def isEffective(self, date):
        # Override DefaultDublinCoreImpl's test, since we are always viewable.
        return 1

    # Ensure portals don't get cataloged.
    def indexObject(self):
        pass

    def unindexObject(self):
        pass

    def reindexObject(self, idxs=None):
        pass

    def reindexObjectSecurity(self, skip_self=False):
        pass

    def UID(self):
        # XXX: workaround that allows the catalog to be cleared and rebuilt,
        # see https://github.com/plone/Products.CMFPlone/issues/3312
        return


# Remove the IContentish interface so we don't listen to events that won't
# apply to the site root, ie handleUidAnnotationEvent
classImplementsOnly(PloneSite, implementedBy(PloneSite) - IContentish)

InitializeClass(PloneSite)
