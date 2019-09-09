# -*- coding: utf-8 -*-
from plone.app.layout.globals.interfaces import IBodyClassAdapter
from plone.app.layout.globals.interfaces import ILayoutPolicy
from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.icons.interfaces import IContentIcon
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.view import memoize
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.controlpanel import ILinkSchema
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
from Products.Five.browser.metaconfigure import ViewMixinForTemplates
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile as ZopeViewPageTemplateFile  # noqa
from zope.component import adapter
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.deprecation import deprecate
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.browser import BrowserView

import json
import six


TEMPLATE_CLASSES = (
    ViewPageTemplateFile,
    ZopeViewPageTemplateFile,
    ViewMixinForTemplates
)


@implementer(ILayoutPolicy)
class LayoutPolicy(BrowserView):
    """A view that gives access to various layout related functions.
    """
    @property
    @memoize
    def _context_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name='plone_context_state'
        )

    def mark_view(self, view):
        """Adds a marker interface to the view if it is "the" view for the
        context May only be called from a template.
        """
        if not view:
            return
        if (
            self._context_state.is_view_template() and
            not IViewView.providedBy(view)
        ):
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
        """Determine whether a column should be shown. The left column is
        called plone.leftcolumn; the right column is called plone.rightcolumn.
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

        renderer = queryMultiAdapter((
            context, self.request, view, manager), IPortletManagerRenderer)
        if renderer is None:
            renderer = getMultiAdapter((
                context, self.request, self, manager), IPortletManagerRenderer)

        return renderer.visible

    @memoize
    def icons_visible(self):
        """Returns True if icons should be shown or False otherwise.
        """
        context = self.context
        membership = getToolByName(context, "portal_membership")
        anon = membership.isAnonymousUser()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISiteSchema, prefix="plone", check=False)
        icon_visibility = settings.icon_visibility

        if icon_visibility == 'enabled':
            return True
        elif icon_visibility == 'authenticated' and not anon:
            return True
        else:
            return False

    @memoize
    def thumb_visible(self):
        """Returns True if thumbs should be shown or False otherwise.
        """
        context = self.context
        membership = getToolByName(context, "portal_membership")
        anon = membership.isAnonymousUser()
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISiteSchema, prefix="plone", check=False)
        thumb_visibility = settings.thumb_visibility

        if thumb_visibility == 'enabled':
            return True
        elif thumb_visibility == 'authenticated' and not anon:
            return True
        else:
            return False

    @deprecate(
        'deprecated since Plone 4, ContentIcons are rendered as Fonts now see'
        'https://docs.plone.org/develop/addons/index.html'
        '#upgrading-to-plone-5-1.'
    )
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

    def _toolbar_classes(self):
        """current toolbar controlling classes
        """
        if not self._context_state.is_toolbar_visible():
            return set()

        toolbar_classes = set()
        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(
            ISiteSchema,
            prefix='plone',
            check=False
        )
        try:
            left = site_settings.toolbar_position == 'side'
        except KeyError:
            left = True
        if left:
            toolbar_classes.add('plone-toolbar-left')
        else:
            toolbar_classes.add('plone-toolbar-top')
        try:
            toolbar_state = {}
            toolbar_state_cookie = self.request.cookies.get('plone-toolbar')
            if toolbar_state_cookie:
                toolbar_state = json.loads(toolbar_state_cookie)
            if toolbar_state.get('expanded', True):
                toolbar_classes.add('plone-toolbar-expanded')
                if left:
                    toolbar_classes.add('plone-toolbar-left-expanded')
                else:
                    toolbar_classes.add('plone-toolbar-top-expanded')
            else:
                if left:
                    toolbar_classes.add('plone-toolbar-left-default')
                else:
                    toolbar_classes.add('plone-toolbar-top-default')
        except Exception:
            pass
        return toolbar_classes

    def bodyClass(self, template, view):
        """
        Returns the CSS class to be used on the body tag.

        Included body classes:
        - template-{}: template name
        - portaltype-{}: portal type
        - site-{}: navigation root
        - section-{}: first section name
        - subsection-{}: subsection names until configured depth
        - icons-on: show icons
        - icons-off: hide icons
        - thumbs-on: show thumbnails
        - thumbs-off: hide thumbnails
        - frontend: user without privileges, no admin interfaces shown
        - viewpermission-{}: minimum permission needed to view context
        - userrole-anonymous: anonymous user
        - userrole-{}: user roles for current user
        - plone-toolbar-left: toolbar is shown on left side
        - plone-toolbar-top: toolbar is shown on top
        - plone-toolbar-expanded: toolbar is in expanded state
        - plone-toolbar-left-expanded: left toolbar is expanded
        - plone-toolbar-top-expanded: top toolbar is expanded
        - plone-toolbar-left-default: left toolbar is not expanded
        - plone-toolbar-top-default: top toolbar is not expanded
        - pat-markspeciallinks: mark special links is set
        """
        portal_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state'
        )
        normalizer = queryUtility(IIDNormalizer)
        registry = getUtility(IRegistry)

        body_classes = self._toolbar_classes()

        # template class (required)
        template_name = ''
        if isinstance(template, TEMPLATE_CLASSES):
            # Browser view
            template_name = view.__name__
        elif template is not None:
            template_name = template.getId()
        elif view:
            # E.g. mosaic, which doesn't pass a template
            template_name = view.__name__
        if template_name:
            template_name = normalizer.normalize(template_name)
            body_classes.add('template-%s' % template_name)

        # portal type class (optional)
        portal_type = normalizer.normalize(self.context.portal_type)
        if portal_type:
            body_classes.add("portaltype-%s" % portal_type)

        # section class (optional)
        navroot = portal_state.navigation_root()
        body_classes.add("site-%s" % navroot.getId())

        contentPath = self.context.getPhysicalPath()[
            len(navroot.getPhysicalPath()):]
        if contentPath:
            body_classes.add("section-%s" % contentPath[0])
            # skip first section since we already have that...
            if len(contentPath) > 1:
                depth = registry.get(
                    'plone.app.layout.globals.bodyClass.depth',
                    4
                )
                if depth > 1:
                    classes = ['subsection-%s' % contentPath[1]]
                    for section in contentPath[2:depth]:
                        classes.append('-'.join([classes[-1], section]))
                    body_classes.update(classes)

        # class for hiding icons (optional)
        if self.icons_visible():
            body_classes.add('icons-on')
        else:
            body_classes.add('icons-off')

        # class for hiding thumbs (optional)
        if self.thumb_visible():
            body_classes.add('thumbs-on')
        else:
            body_classes.add('thumbs-off')

        # permissions required. Useful to theme frontend and backend
        # differently
        permissions = []
        if not getattr(view, '__ac_permissions__', tuple()):
            permissions = ['none']
        for permission, roles in getattr(view, '__ac_permissions__', tuple()):
            permissions.append(normalizer.normalize(permission))
        if 'none' in permissions or 'view' in permissions:
            body_classes.add('frontend')
        for permission in permissions:
            body_classes.add('viewpermission-' + permission)

        # class for user roles
        membership = getToolByName(self.context, "portal_membership")
        if membership.isAnonymousUser():
            body_classes.add('userrole-anonymous')
        else:
            user = membership.getAuthenticatedMember()
            for role in user.getRolesInContext(self.context):
                body_classes.add(
                    'userrole-' + role.lower().replace(' ', '-')
                )

        # class for markspeciallinks pattern
        link_settings = registry.forInterface(
            ILinkSchema,
            prefix="plone",
            check=False
        )
        msl = link_settings.mark_special_links
        elonw = link_settings.external_links_open_new_window
        if msl or elonw:
            body_classes.add('pat-markspeciallinks')

        # Add externally defined extra body classes
        body_class_adapters = getAdapters(
            (self.context, self.request),
            IBodyClassAdapter
        )
        for name, body_class_adapter in body_class_adapters:
            try:
                extra_classes = body_class_adapter.get_classes(template, view) or []
            except TypeError:  # This adapter is implemented without arguments
                extra_classes = body_class_adapter.get_classes() or []
            if isinstance(extra_classes, six.string_types):
                extra_classes = extra_classes.split(' ')
            body_classes.update(extra_classes)

        return ' '.join(sorted(body_classes))


@adapter(Interface)
@implementer(IBodyClassAdapter)
class DefaultBodyClasses(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_classes(self, template, view):
        """Default body classes adapter.
        """
        return []
