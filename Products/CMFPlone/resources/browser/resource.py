from ..webresource import PloneScriptResource
from ..webresource import PloneStyleResource
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from App.config import getConfiguration
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.theming.interfaces import IThemeSettings
from plone.app.theming.utils import theming_policy
from plone.registry.interfaces import IRegistry
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IBundleRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.ramcache.interfaces import ram

import webresource


REQUEST_CACHE_KEY = "_WEBRESOURCE_CACHE_"


class ResourceBase:
    """Information for script rendering.

    This is a mixin base class for a browser view, a viewlet or a tile
    or anything similar with a context and a request set on initialization.
    """

    @property
    def _rendered_cache(self):
        if getConfiguration().debug_mode:
            return
        self.registry = getUtility(IRegistry)
        if not self.registry["plone.resources.development"]:
            return getattr(
                self.context, f"_v_renderend_cached_{self.__class__.__name__}", None
            )

    @_rendered_cache.setter
    def _rendered_cache(self, value):
        setattr(self.context, f"_v_renderend_cached_{self.__class__.__name__}", value)

    def update(self):
        # cache on request
        cached = getattr(self.request, REQUEST_CACHE_KEY, None)
        if cached is not None:
            self.renderer = cached
            return

        # prepare
        self.portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        if not getattr(self, "registry", None):
            self.registry = getUtility(IRegistry)
        theme = None
        policy = theming_policy(self.request)
        if policy.isThemeEnabled():
            # Check if Diazo is enabled
            theme = policy.get_theme() or None

        # we have two groups for two viewlets (historical reasons)
        root_group_js = webresource.ResourceGroup(name="root_js")
        root_group_css = webresource.ResourceGroup(name="root_css")

        # register all bundles from registry
        registry_group_js = webresource.ResourceGroup(
            name="registry_js", group=root_group_js
        )
        registry_group_css = webresource.ResourceGroup(
            name="registry_css", group=root_group_css
        )
        records = self.registry.collectionOfInterface(
            IBundleRegistry, prefix="plone.bundles", check=False
        )
        unique = True

        theme_enabled_bundles = getattr(theme, "enabled_bundles", [])
        theme_disabled_bundles = getattr(theme, "disabled_bundles", [])

        # include sub/parent request
        request = self.request
        request_enabled_bundles = set(getattr(request, "enabled_bundles", []))
        request_disabled_bundles = set(getattr(request, "disabled_bundles", []))
        while request.get("PARENT_REQUEST", None):
            request = request["PARENT_REQUEST"]
            request_enabled_bundles.update(getattr(request, "enabled_bundles", []))
            request_disabled_bundles.update(getattr(request, "disabled_bundles", []))

        for name, record in records.items():
            include = record.enabled
            include = include or name in theme_enabled_bundles
            include = include and name not in theme_disabled_bundles
            include = include or name in request_enabled_bundles
            include = include and name not in request_disabled_bundles

            if include and record.expression:

                def current_expression():
                    return self.eval_expression(record.expression, name)

                include = current_expression
            if record.jscompilation:
                external = record.jscompilation.startswith("http")
                resource = PloneScriptResource(
                    context=self.context,
                    name=name,
                    depends=record.depends or "",
                    resource=record.jscompilation if not external else None,
                    compressed=record.jscompilation if not external else None,
                    include=include,
                    unique=unique,
                    group=registry_group_js,
                    url=record.jscompilation if external else None,
                    crossorigin="anonymous" if external else None,
                    async_=record.load_async or None,
                    defer=record.load_defer or None,
                    integrity=not external,
                )
            if record.csscompilation:
                external = record.csscompilation.startswith("http")
                resource = PloneStyleResource(
                    context=self.context,
                    name=name,
                    depends=record.depends or "",
                    resource=record.csscompilation if not external else None,
                    compressed=record.csscompilation if not external else None,
                    include=include,
                    unique=unique,
                    group=registry_group_css,
                    url=record.csscompilation if external else None,
                    media="all",
                    rel="stylesheet",
                )

        # Collect theme data
        themedata = {}
        themedata["production_css"] = getattr(theme, "production_css", None)
        themedata["development_css"] = getattr(theme, "development_css", None)
        themedata["production_js"] = getattr(theme, "production_js", None)
        themedata["development_js"] = getattr(theme, "development_js", None)

        # add Theme JS
        if themedata["production_js"]:
            # we ignore development_js for external detection
            external = themedata["production_js"].startswith("http")
            PloneScriptResource(
                context=self.context,
                name="theme",
                depends="",
                resource=(
                    themedata["development_js"] or themedata["production_js"]
                    if not external
                    else None
                ),
                compressed=themedata["production_js"] if not external else None,
                include=True,
                unique=unique,
                group=root_group_js,
                url=themedata["production_js"] if external else None,
                crossorigin="anonymous" if external else None,
                integrity=not external,
            )

        # add Theme CSS
        if themedata["production_css"]:
            # we ignore development_css for external detection
            external = themedata["production_css"].startswith("http")
            PloneStyleResource(
                context=self.context,
                name="theme",
                depends="",
                resource=(
                    themedata["development_css"] or themedata["production_css"]
                    if not external
                    else None
                ),
                compressed=themedata["production_css"] if not external else None,
                include=True,
                unique=unique,
                group=root_group_css,
                url=themedata["production_css"] if external else None,
                media="all",
                rel="stylesheet",
            )

        # add Custom CSS
        registry = getUtility(IRegistry)
        theme_settings = registry.forInterface(IThemeSettings, False)
        if theme_settings.custom_css:
            PloneStyleResource(
                context=self.context,
                name="custom",
                depends="",
                resource="@@custom.css",
                include=True,
                unique=unique,
                group=root_group_css,
                media="all",
                rel="stylesheet",
            )

        self.renderer = {}
        setattr(self.request, REQUEST_CACHE_KEY, self.renderer)
        resolver_js = webresource.ResourceResolver(root_group_js)
        self.renderer["js"] = webresource.ResourceRenderer(
            resolver_js, base_url=self.portal_state.portal_url()
        )
        resolver_css = webresource.ResourceResolver(root_group_css)
        self.renderer["css"] = webresource.ResourceRenderer(
            resolver_css, base_url=self.portal_state.portal_url()
        )

    def evaluateExpression(self, expression, context):
        """Evaluate an object's TALES condition to see if it should be
        displayed.
        """
        try:
            if expression.text and context is not None:
                portal = getToolByName(context, "portal_url").getPortalObject()

                # Find folder (code courtesy of CMFCore.ActionsTool)
                if context is None or not hasattr(context, "aq_base"):
                    folder = portal
                else:
                    folder = context
                    # Search up the containment hierarchy until we find an
                    # object that claims it's PrincipiaFolderish.
                    while folder is not None:
                        if getattr(aq_base(folder), "isPrincipiaFolderish", 0):
                            # found it.
                            break
                        else:
                            folder = aq_parent(aq_inner(folder))

                __traceback_info__ = (folder, portal, context, expression)
                ec = createExprContext(folder, portal, context)
                # add 'context' as an alias for 'object'
                ec.setGlobal("context", context)
                return expression(ec)
            return True
        except AttributeError:
            return True

    def eval_expression(self, expression, bundle_name):
        if not expression:
            return True
        cache = queryUtility(ram.IRAMCache)
        cooked_expression = None
        if cache is not None:
            cooked_expression = cache.query(
                "plone.bundles.cooked_expressions",
                key=dict(prefix=bundle_name),
                default=None,
            )
        if cooked_expression is None or cooked_expression.text != expression:
            cooked_expression = Expression(expression)
            if cache is not None:
                cache.set(
                    cooked_expression,
                    "plone.bundles.cooked_expressions",
                    key=dict(prefix=bundle_name),
                )
        return self.evaluateExpression(cooked_expression, self.context)


class ResourceView(ResourceBase, ViewletBase):
    """Viewlet Information for script rendering."""


class ScriptsView(ResourceView):
    """Script Viewlet."""

    def index(self):
        rendered = self._rendered_cache
        if not rendered:
            rendered = self.renderer["js"].render()
            self._rendered_cache = rendered
        return rendered


class StylesView(ResourceView):
    """Styles Viewlet"""

    def index(self):
        rendered = self._rendered_cache
        if not rendered:
            rendered = self.renderer["css"].render()
            self._rendered_cache = rendered
        return rendered
