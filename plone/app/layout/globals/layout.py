from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.view import memoize
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implements
from zope.publisher.browser import BrowserView

from AccessControl import Unauthorized
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile as ZopeViewPageTemplateFile

from plone.app.layout.globals.interfaces import ILayoutPolicy
from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.icons.interfaces import IContentIcon


class LayoutPolicy(BrowserView):
    """A view that gives access to various layout related functions.
    """

    implements(ILayoutPolicy)

    def mark_view(self, view):
        """Adds a marker interface to the view if it is "the" view for the
        context May only be called from a template.
        """
        if not view:
            return

        context_state = getMultiAdapter(
            (self.context, self.request), name=u'plone_context_state')

        if context_state.is_view_template() and not IViewView.providedBy(view):
            alsoProvides(view, IViewView)

    def hide_columns(self, column_left, column_right):
        """Returns a CSS class matching the current column status.
        """
        if not column_right and not column_left:
            return "visualColumnHideOneTwo"
        if column_right and not column_left:
            return "visualColumnHideOne"
        if not column_right and column_left:
            return "visualColumnHideTwo"
        return "visualColumnHideNone"

    def have_portlets(self, manager_name, view=None):
        """Determine whether a column should be shown. The left column is called
        plone.leftcolumn; the right column is called plone.rightcolumn.
        """
        force_disable = self.request.get('disable_' + manager_name, None)
        if force_disable is not None:
            return not bool(force_disable)

        context = self.context
        if view is None:
            view = self

        manager = queryUtility(IPortletManager, name=manager_name)
        if manager is None:
            return False

        renderer = queryMultiAdapter((context, self.request, view, manager), IPortletManagerRenderer)
        if renderer is None:
            renderer = getMultiAdapter((context, self.request, self, manager), IPortletManagerRenderer)

        return renderer.visible

    @memoize
    def icons_visible(self):
        """Returns True if icons should be shown or False otherwise.
        """
        context = self.context
        membership = getToolByName(context, "portal_membership")
        properties = getToolByName(context, "portal_properties")

        site_properties = getattr(properties, 'site_properties')
        icon_visibility = site_properties.getProperty('icon_visibility', 'enabled')

        if icon_visibility == 'enabled':
            return True
        elif icon_visibility == 'authenticated' and not membership.isAnonymousUser():
            return True
        else:
            return False

    def getIcon(self, item):
        """Returns an object which implements the IContentIcon interface and
        provides the informations necessary to render an icon. The item
        parameter needs to be adaptable to IContentIcon. Icons can be disabled
        globally or just for anonymous users with the icon_visibility property
        in site_properties.
        """
        context = self.context
        if not self.icons_visible():
            icon = getMultiAdapter((context, self.request, None), IContentIcon)
        else:
            icon = getMultiAdapter((context, self.request, item), IContentIcon)
        return icon

    def renderBase(self):
        """Returns the current URL to be used in the base tag.
        """
        context = self.context
        # when accessing via WEBDAV you're not allowed to access aq_base
        try:
            if getattr(aq_base(context), 'isPrincipiaFolderish', False):
                return context.absolute_url() + '/'
        except Unauthorized:
            pass
        return context.absolute_url()

    def bodyClass(self, template, view):
        """Returns the CSS class to be used on the body tag.
        """
        context = self.context
        portal_state = getMultiAdapter(
            (context, self.request), name=u'plone_portal_state')

        # template class (required)
        name = ''
        if isinstance(template, ViewPageTemplateFile) or \
           isinstance(template, ZopeViewPageTemplateFile):
            # Browser view
            name = view.__name__
        else:
            name = template.getId()
        body_class = 'template-%s' % name

        # portal type class (optional)
        normalizer = queryUtility(IIDNormalizer)
        portal_type = normalizer.normalize(context.portal_type)
        if portal_type:
            body_class += " portaltype-%s" % portal_type

        # section class (optional)
        navroot = portal_state.navigation_root()
        body_class += " site-%s" % navroot.getId()

        contentPath = context.getPhysicalPath()[len(navroot.getPhysicalPath()):]
        if contentPath:
            body_class += " section-%s" % contentPath[0]

        # class for hiding icons (optional)
        if self.icons_visible():
            body_class += ' icons-on'

        return body_class
