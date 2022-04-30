from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.base.i18nl10n import ulocalized_time
from plone.memoize.view import memoize
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import IPlone
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.deprecation import deprecate
from zope.i18n import translate
from zope.interface import implementer
from zope.size import byteDisplay


_marker = []


@implementer(IPlone)
class Plone(BrowserView):

    # Utility methods

    @memoize
    @deprecate("Unused. Will be removed in Plone 6.1")
    def uniqueItemIndex(self, pos=0):
        """Return an index iterator."""
        return utils.RealIndexIterator(pos=pos)

    def toLocalizedTime(self, time, long_format=None, time_only=None):
        """Convert time to localized time
        """
        return ulocalized_time(
            time,
            long_format,
            time_only,
            aq_inner(self.context),
            'plonelocales',
            self.request,
        )

    def toLocalizedSize(self, size):
        """Convert an integer to a localized size string
        """
        return translate(byteDisplay(size), context=self.request)

    # This can't be request-memoized, because it won't necessarily remain
    # valid across traversals. For example, you may get tabs on an error
    # message.
    @deprecate("Unused. Will be removed in Plone 6.1")
    def showToolbar(self):
        """Determine if the editable border should be shown
        """
        request = self.request
        if 'disable_border' in request or 'disable_toolbar' in request:
            return False
        if 'enable_border' in request or 'enable_toolbar' in request:
            return True

        context = aq_inner(self.context)

        portal_membership = getToolByName(context, 'portal_membership')
        checkPerm = portal_membership.checkPermission

        if (checkPerm('Modify portal content', context) or
            checkPerm('Add portal content', context) or
                checkPerm('Review portal content', context)):
            return True

        if portal_membership.isAnonymousUser():
            return False

        context_state = getMultiAdapter(
            (context, request),
            name="plone_context_state"
        )
        actions = context_state.actions

        if actions('workflow', max=1):
            return True

        if actions('batch', max=1):
            return True

        for action in actions('object'):
            if action.get('id', '') != 'view':
                return True

        template_id = None
        if 'PUBLISHED' in request:
            if getattr(request['PUBLISHED'], 'getId', None):
                template_id = request['PUBLISHED'].getId()

        idActions = {}
        for obj in actions('object') + actions('folder'):
            idActions[obj.get('id', '')] = 1

        if 'edit' in idActions:
            if (template_id in idActions or
                template_id in ['synPropertiesForm', 'folder_contents',
                                'folder_listing', 'listing_view']):
                return True

        # Check to see if the user is able to add content
        allowedTypes = context.allowedContentTypes()
        return bool(allowedTypes)

    def normalizeString(self, text):
        """Normalizes a title to an id.
        """
        return utils.normalizeString(text, context=self)

    def cropText(self, text, length, ellipsis='...'):
        """Crop text on a word boundary
        """
        if not length:
            return text
        converted = False
        if not isinstance(text, str):
            text = utils.safe_text(text)
            converted = True
        if len(text) > length:
            text = text[:length]
            l = text.rfind(' ')
            if l > length / 2:
                text = text[:l + 1]
            text += ellipsis
        if converted:
            # encode back from unicode
            text = text.encode('utf-8')
        return text

    @property
    def human_readable_size(self):
        return utils.human_readable_size

    @memoize
    def patterns_settings(self):
        context = aq_inner(self.context)
        return getMultiAdapter(
            (context, self.request),
            name='plone_patterns_settings')()

    @deprecate("Superfluous - it returns always 'utf-8'")
    def site_encoding(self):
        return 'utf-8'

    @deprecate("use getCurrentUrl on @@plone_context_state instead (will be removed in Plone 7)")
    def getCurrentUrl(self):
        context_state = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name='plone_context_state')
        return context_state.current_page_url()

    @deprecate("use isDefaultPageInFolder on @@plone_context_state instead (will be removed in Plone 7)")
    def isDefaultPageInFolder(self):
        context_state = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name='plone_context_state')
        return context_state.is_default_page()

    @deprecate("use isStructuralFolder on @@plone_context_state instead (will be removed in Plone 7)")
    def isStructuralFolder(self):
        context_state = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name='plone_context_state')
        return context_state.is_structural_folder()

    @deprecate("use navigationRootPath on @@plone_portal_state instead (will be removed in Plone 7)")
    def navigationRootPath(self):
        portal_state = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name='plone_portal_state')
        return portal_state.navigation_root_path()

    @deprecate("use navigationRootUrl @@plone_portal_state instead (will be removed in Plone 7)")
    def navigationRootUrl(self):
        portal_state = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name='plone_portal_state')
        return portal_state.navigation_root_url()

    # would need some love to get rid of many verbose deprecation warning, skip for now.
    #@deprecate("use getParentObject on @@plone_context_state instead (will be removed in Plone 7)")
    def getParentObject(self):
        return aq_parent(aq_inner(self.context))

    @deprecate("use getCurrentFolder on @@plone_context_state instead (will be removed in Plone 7)")
    def getCurrentFolder(self):
        context_state = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name='plone_context_state')
        return context_state.folder()

    @deprecate("use getCurrentFolderUrl on @@plone_context_state instead (will be removed in Plone 7)")
    def getCurrentFolderUrl(self):
        context_state = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name='plone_context_state')
        return context_state.folder().absolute_url()

    @memoize
    @deprecate("use getCurrentObjectUrl on @@plone_context_state instead (will be removed in Plone 7)")
    def getCurrentObjectUrl(self):
        context_state = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name='plone_context_state')
        return context_state.canonical_object_url()

    @memoize
    @deprecate("use getCurrentObjectUrl on @@plone_context_state instead (will be removed in Plone 7)")
    def isFolderOrFolderDefaultPage(self):
        state = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name='plone_context_state')
        return state.is_structural_folder() or state.is_default_page()

    @memoize
    @deprecate("use isPortalOrPortalDefaultPage on @@plone_context_state instead (will be removed in Plone 7)")
    def isPortalOrPortalDefaultPage(self):
        context_state = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name='plone_context_state')
        return context_state.is_portal_root()

    @memoize
    @deprecate("use getViewTemplateId on @@plone_context_state instead (will be removed in Plone 7)")
    def getViewTemplateId(self):
        context_state = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name='plone_context_state')
        return context_state.view_template_id()


