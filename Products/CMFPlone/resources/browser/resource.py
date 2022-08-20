from ..webresource import PloneScriptResource
from ..webresource import PloneStyleResource
from App.config import getConfiguration
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.theming.interfaces import IThemeSettings
from plone.app.theming.utils import theming_policy
from plone.base.interfaces import IBundleRegistry
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite

import hashlib
import logging
import webresource


logger = logging.getLogger(__name__)

REQUEST_CACHE_KEY = "_WEBRESOURCE_CACHE_"

GRACEFUL_DEPENDENCY_REWRITE = {
    "plone-base": "plone",
    "plone-legacy": "plone",
    "plone-logged-in": "plone",
}


class ResourceBase:
    """Information for script rendering.

    This is a mixin base class for a browser view, a viewlet or a tile
    or anything similar with a context and a request set on
    initialization.
    """

    def _request_bundles(self):
        request = self.request
        request_enabled_bundles = set(getattr(request, "enabled_bundles", []))
        request_disabled_bundles = set(getattr(request, "disabled_bundles", []))
        # include sub/parent request
        while request.get("PARENT_REQUEST", None):
            request = request["PARENT_REQUEST"]
            request_enabled_bundles.update(getattr(request, "enabled_bundles", []))
            request_disabled_bundles.update(getattr(request, "disabled_bundles", []))
        return request_enabled_bundles, request_disabled_bundles

    def _cache_attr_name(self, site):
        hashtool = hashlib.sha256()
        hashtool.update(self.__class__.__name__.encode('utf8'))
        hashtool.update(site.absolute_url().encode('utf8'))
        e_bundles, d_bundles = self._request_bundles()
        for bundle in e_bundles | d_bundles:
            hashtool.update(bundle.encode('utf8'))
        return f"_v_renderend_cache_{hashtool.hexdigest()}"

    @property
    def _rendered_cache(self):
        if getConfiguration().debug_mode:
            return
        self.registry = getUtility(IRegistry)
        if not self.registry["plone.resources.development"]:
            site = getSite()
            return getattr(site, self._cache_attr_name(site), None)

    @_rendered_cache.setter
    def _rendered_cache(self, value):
        site = getSite()
        setattr(site, self._cache_attr_name(site), value)

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
        request_enabled_bundles, request_disabled_bundles = self._request_bundles()

        # collect names
        js_names = [name for name, rec in records.items() if rec.jscompilation]
        css_names = [name for name, rec in records.items() if rec.csscompilation]
        all_names = [
            name
            for name, rec in records.items()
            if rec.jscompilation or rec.csscompilation
        ]

        def check_dependencies(bundle_name, depends, bundles):
            # "depends" can be a comma separated string of dependent
            # bundle names
            depend_names = depends.split(",") if depends else []
            valid_dependencies = []

            for name in depend_names:
                if name in bundles:
                    valid_dependencies.append(name)
                    continue
                if name in all_names:
                    # ignore dependency on bundle outside "bundles"
                    continue

                msg = f"Bundle '{bundle_name}' has a non existing dependency on '{name}'. "

                if name in GRACEFUL_DEPENDENCY_REWRITE:
                    # gracefully rewrite old bundle names
                    graceful_depends = GRACEFUL_DEPENDENCY_REWRITE[name]
                    logger.error(
                            msg
                            + f"Bundle dependency graceful rewritten to '{graceful_depends}' "
                            + "Fallback will be removed in Plone 7."
                        )
                    valid_dependencies.append(graceful_depends)
                    continue

                # if the dependency does not exist, skip the bundle
                logger.error(
                    msg + "Bundle ignored - This may break your site!"
                )
                return "__broken__"

            return valid_dependencies

        # register
        for name, record in records.items():
            include = record.enabled
            include = include or name in theme_enabled_bundles
            include = include and name not in theme_disabled_bundles
            include = include or name in request_enabled_bundles
            include = include and name not in request_disabled_bundles

            if record.jscompilation:
                depends = check_dependencies(name, record.depends, js_names)
                if depends == "__broken__":
                    continue
                external = record.jscompilation.startswith("http")
                PloneScriptResource(
                    context=self.context,
                    name=name,
                    depends=depends,
                    resource=record.jscompilation if not external else None,
                    compressed=record.jscompilation if not external else None,
                    include=include,
                    expression=record.expression,
                    unique=unique,
                    group=registry_group_js,
                    url=record.jscompilation if external else None,
                    crossorigin="anonymous" if external else None,
                    async_=record.load_async or None,
                    defer=record.load_defer or None,
                    integrity=not external,
                )
            if record.csscompilation:
                depends = check_dependencies(name, record.depends, css_names)
                if depends == "__broken__":
                    continue
                external = record.csscompilation.startswith("http")
                PloneStyleResource(
                    context=self.context,
                    name=name,
                    depends=depends,
                    resource=record.csscompilation if not external else None,
                    compressed=record.csscompilation if not external else None,
                    include=include,
                    expression=record.expression,
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
    """Styles Viewlet."""

    def index(self):
        rendered = self._rendered_cache
        if not rendered:
            rendered = self.renderer["css"].render()
            self._rendered_cache = rendered
        return rendered
