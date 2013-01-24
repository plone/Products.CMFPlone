from Products.CMFDefault.Portal import CMFSite

from Products.CMFCore import permissions
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.PloneFolder import OrderedContainer

from AccessControl import ClassSecurityInfo
from AccessControl import Permissions
from AccessControl import Unauthorized
from Acquisition import aq_base
from App.class_init import InitializeClass
from ComputedAttribute import ComputedAttribute
from webdav.NullResource import NullResource
from Products.CMFPlone.PloneFolder import ReplaceableWrapper
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.interfaces.syndication import ISyndicatable

from plone.i18n.locales.interfaces import IMetadataLanguageAvailability
from zope.interface import implements
from zope.component import queryUtility

member_indexhtml = """\
member_search=context.restrictedTraverse('member_search_form')
return member_search()
"""


class PloneSite(CMFSite, OrderedContainer, BrowserDefaultMixin, UniqueObject):
    """Make PloneSite subclass CMFSite and add some methods."""

    security = ClassSecurityInfo()
    meta_type = portal_type = 'Plone Site'

    implements(IPloneSiteRoot, ISyndicatable)

    manage_options = (
        CMFSite.manage_options[:2] +
        CMFSite.manage_options[3:]
        )

    __ac_permissions__ = tuple(list(CMFSite.__ac_permissions__) +
        [('Modify portal content',
         ('manage_cutObjects', 'manage_pasteObjects',
          'manage_renameForm', 'manage_renameObject',
          'manage_renameObjects'))])

    security.declareProtected(Permissions.copy_or_move, 'manage_copyObjects')

    manage_renameObject = OrderedContainer.manage_renameObject

    moveObject = OrderedContainer.moveObject
    moveObjectsByDelta = OrderedContainer.moveObjectsByDelta

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

    def __browser_default__(self, request):
        """ Set default so we can return whatever we want instead
        of index_html """
        return getToolByName(self, 'plone_utils').browserDefault(self)

    def index_html(self):
        """ Acquire if not present. """
        request = getattr(self, 'REQUEST', None)
        if request is not None and 'REQUEST_METHOD' in request:
            if request.maybe_webdav_client:
                method = request['REQUEST_METHOD']
                if method in ('PUT', ):
                    # Very likely a WebDAV client trying to create something
                    return ReplaceableWrapper(NullResource(self, 'index_html'))
                elif method in ('GET', 'HEAD', 'POST'):
                    # Do nothing, let it go and acquire.
                    pass
                else:
                    raise AttributeError('index_html')
        # Acquire from skin.
        _target = self.__getattr__('index_html')
        return ReplaceableWrapper(aq_base(_target).__of__(self))

    index_html = ComputedAttribute(index_html, 1)

    def manage_beforeDelete(self, container, item):
        """ Should send out an Event before Site is being deleted """
        self.removal_inprogress = 1
        PloneSite.inheritedAttribute('manage_beforeDelete')(self, container,
                                                            item)

    security.declareProtected(permissions.DeleteObjects, 'manage_delObjects')
    def manage_delObjects(self, ids=None, REQUEST=None):
        """We need to enforce security."""
        if ids is None:
            ids = []
        if isinstance(ids, basestring):
            ids = [ids]
        for id in ids:
            item = self._getOb(id)
            if not _checkPermission(permissions.DeleteObjects, item):
                raise Unauthorized(
                    "Do not have permissions to remove this object")
        return CMFSite.manage_delObjects(self, ids, REQUEST=REQUEST)

    def view(self):
        """ Ensure that we get a plain view of the object, via a delegation to
        __call__(), which is defined in BrowserDefaultMixin
        """
        return self()

    security.declareProtected(permissions.AccessContentsInformation,
                              'folderlistingFolderContents')

    def folderlistingFolderContents(self, contentFilter=None):
        """Calls listFolderContents in protected only by ACI so that
        folder_listing can work without the List folder contents permission,
        as in CMFDefault.

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
        languages.insert(0, (u'', _(u'Language neutral (site default)')))
        return languages

    # Ensure portals don't get cataloged.
    def indexObject(self):
        pass

    def unindexObject(self):
        pass

    def reindexObject(self, idxs=None):
        if idxs is None:
            idxs = []
        pass

    def reindexObjectSecurity(self, skip_self=False):
        pass

InitializeClass(PloneSite)
