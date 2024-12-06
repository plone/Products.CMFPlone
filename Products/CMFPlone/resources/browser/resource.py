from ..webresource import PloneScriptResource
from ..webresource import PloneStyleResource
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.theming.interfaces import IThemeSettings
from plone.app.theming.utils import theming_policy
from plone.base.interfaces import IBundleRegistry
from plone.registry.interfaces import IRegistry
from time import time
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility

import logging
import webresource


logger = logging.getLogger(__name__)

REQUEST_CACHE_KEY = "_WEBRESOURCE_CACHE_"
_RESOURCE_REGISTRY_MTIME = "__RESOURCE_REGISTRY_MTIME"
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

    @staticmethod
    def is_external_url(resource):
        # we check if the resource string starts with http and //
        # according to relative URI definition in
        # https://www.ietf.org/rfc/rfc3986.txt chapter 4.2
        return resource.startswith("http") or resource.startswith("//")

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

    def update(self):
        # cache on request
        cached = getattr(self.request, REQUEST_CACHE_KEY, None)
        if cached is not None:
            self.rendered = cached
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
        registry_group_js_deferred = webresource.ResourceGroup(
            name="registry_js_deferred",
        )
        registry_group_css = webresource.ResourceGroup(
            name="registry_css", group=root_group_css
        )
        registry_group_css_deferred = webresource.ResourceGroup(
            name="registry_css_deferred",
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
                if name in bundles or name == "all":
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
                logger.error(msg + "Bundle ignored - This may break your site!")
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
                external = self.is_external_url(record.jscompilation)
                r_group = registry_group_js
                if "all" in depends:
                    # move to a separate group which is rendered after all others
                    r_group = registry_group_js_deferred
                    depends = None
                PloneScriptResource(
                    context=self.context,
                    name=name,
                    depends=depends,
                    resource=record.jscompilation if not external else None,
                    compressed=record.jscompilation if not external else None,
                    include=include,
                    expression=record.expression,
                    unique=unique,
                    group=r_group,
                    url=record.jscompilation if external else None,
                    crossorigin="anonymous" if external else None,
                    async_=record.load_async or None,
                    defer=record.load_defer or None,
                    integrity=not external,
                    **{"data-bundle": name},
                )
            if record.csscompilation:
                depends = check_dependencies(name, record.depends, css_names)
                if depends == "__broken__":
                    continue
                external = self.is_external_url(record.csscompilation)
                r_group = registry_group_css
                if "all" in depends:
                    # move to a separate group which is rendered after all others
                    r_group = registry_group_css_deferred
                    depends = None
                PloneStyleResource(
                    context=self.context,
                    name=name,
                    depends=depends,
                    resource=record.csscompilation if not external else None,
                    compressed=record.csscompilation if not external else None,
                    include=include,
                    expression=record.expression,
                    unique=unique,
                    group=r_group,
                    url=record.csscompilation if external else None,
                    media="all",
                    rel="stylesheet",
                    **{"data-bundle": name},
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
            external = self.is_external_url(themedata["production_js"])
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
                **{"data-bundle": "diazo"},
            )

        # add Theme CSS
        if themedata["production_css"]:
            # we ignore development_css for external detection
            external = self.is_external_url(themedata["production_css"])
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
                **{"data-bundle": "diazo"},
            )

        # add "deferred" groups at this point
        root_group_js.add(registry_group_js_deferred)
        root_group_css.add(registry_group_css_deferred)

        # add Custom CSS always after everything else
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
                **{"data-bundle": "plonecustomcss"},
            )

        self.rendered = {}
        setattr(self.request, REQUEST_CACHE_KEY, self.rendered)
        resolver_js = webresource.ResourceResolver(root_group_js)
        self.rendered["js"] = webresource.ResourceRenderer(
            resolver_js, base_url=self.portal_state.portal_url()
        ).render()
        resolver_css = webresource.ResourceResolver(root_group_css)
        self.rendered["css"] = webresource.ResourceRenderer(
            resolver_css, base_url=self.portal_state.portal_url()
        ).render()


class ResourceView(ResourceBase, ViewletBase):
    """Viewlet Information for resource rendering."""


class ScriptsView(ResourceView):
    """Script Viewlet."""

    def index(self):
        return self.rendered["js"]


class StylesView(ResourceView):
    """Styles Viewlet."""

    def index(self):
        return self.rendered["css"]


def update_resource_registry_mtime():
    """Update the last modification time of the resource registry.

    Call this when you change anything that may influence the resource registry
    and any of its rendered cache.
    See discussion in https://github.com/plone/Products.CMFPlone/issues/3505
    and https://github.com/plone/Products.CMFPlone/pull/3771
    """
    registry = queryUtility(IRegistry)
    if registry is None:
        # This can happen for example during site creation.
        return
    setattr(registry, _RESOURCE_REGISTRY_MTIME, time())
    logger.info("Updated resource registry mtime.")
