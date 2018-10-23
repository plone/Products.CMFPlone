# -*- coding: utf-8 -*-
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from App.config import getConfiguration
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.theming.utils import theming_policy
from plone.memoize.view import memoize
from plone.registry.interfaces import IRegistry
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import _getAuthenticatedUser
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IBundleRegistry
from Products.CMFPlone.interfaces import IResourceRegistry
from Products.CMFPlone.resources import RESOURCE_DEVELOPMENT_MODE
from Products.CMFPlone.resources.browser.combine import get_production_resource_directory  # noqa
from Products.CMFPlone.resources.bundle import Bundle
from Products.CMFPlone.utils import get_top_request
from zope import component
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.ramcache.interfaces import ram


class ResourceBase(object):
    """Information for script rendering.

    This is a mixin base class for a browser view, a viewlet or a tile
    or anything similar with a context and a request set on initialization.
    """

    @property
    @memoize
    def anonymous(self):
        return _getAuthenticatedUser(
            self.context
        ).getUserName() == 'Anonymous User'

    @property
    @memoize
    def development(self):
        """
        To set development mode:

        - we can define a envvar: FEDEV
        - otherwise if its anonymous is using production mode
        - finally is checked on the registry entry
        """
        if RESOURCE_DEVELOPMENT_MODE:
            return True
        if self.anonymous and not self.debug_mode:
            return False
        return self.registry.records['plone.resources.development'].value

    @property
    def debug_mode(self):
        return getConfiguration().debug_mode

    def develop_bundle(self, bundle, attr):
        return (
            RESOURCE_DEVELOPMENT_MODE or
            (self.development and getattr(bundle, attr, False))
        )

    @property
    def last_legacy_import(self):
        return self.registry.records['plone.resources.last_legacy_import'].value  # noqa

    def evaluateExpression(self, expression, context):
        """Evaluate an object's TALES condition to see if it should be
        displayed.
        """
        try:
            if expression.text and context is not None:
                portal = getToolByName(context, 'portal_url').getPortalObject()

                # Find folder (code courtesy of CMFCore.ActionsTool)
                if context is None or not hasattr(context, 'aq_base'):
                    folder = portal
                else:
                    folder = context
                    # Search up the containment hierarchy until we find an
                    # object that claims it's PrincipiaFolderish.
                    while folder is not None:
                        if getattr(aq_base(folder), 'isPrincipiaFolderish', 0):
                            # found it.
                            break
                        else:
                            folder = aq_parent(aq_inner(folder))

                __traceback_info__ = (folder, portal, context, expression)
                ec = createExprContext(folder, portal, context)
                # add 'context' as an alias for 'object'
                ec.setGlobal('context', context)
                return expression(ec)
            else:
                return True
        except AttributeError:
            return True

    def update(self):
        self.portal_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state'
        )
        self.site_url = self.portal_state.portal_url()
        self.registry = getUtility(IRegistry)
        self.production_path = get_production_resource_directory()

        theme = None
        policy = theming_policy(self.request)
        if policy.isThemeEnabled():
            # Check if Diazo is enabled
            theme = policy.get_theme() or None

        self.diazo_production_css = getattr(theme, 'production_css', None)
        self.diazo_development_css = getattr(theme, 'development_css', None)
        self.diazo_production_js = getattr(theme, 'production_js', None)
        self.diazo_development_js = getattr(theme, 'development_js', None)
        self.theme_enabled_bundles = getattr(theme, 'enabled_bundles', [])
        self.theme_disabled_bundles = getattr(theme, 'disabled_bundles', [])

    def get_bundles(self):
        result = {}
        records = self.registry.collectionOfInterface(
            IBundleRegistry,
            prefix="plone.bundles",
            check=False
        )
        for name, record in records.items():
            result[name] = Bundle(record)
        return result

    def get_resources(self):
        return self.registry.collectionOfInterface(
            IResourceRegistry,
            prefix="plone.resources",
            check=False
        )

    def eval_expression(self, expression, bundle_name):
        if not expression:
            return True
        cache = component.queryUtility(ram.IRAMCache)
        cooked_expression = None
        if cache is not None:
            cooked_expression = cache.query(
                'plone.bundles.cooked_expressions',
                key=dict(prefix=bundle_name),
                default=None
            )
        if (
            cooked_expression is None or
            cooked_expression.text != expression
        ):
            cooked_expression = Expression(expression)
            if cache is not None:
                cache.set(
                    cooked_expression,
                    'plone.bundles.cooked_expressions',
                    key=dict(prefix=bundle_name)
                )
        return self.evaluateExpression(cooked_expression, self.context)

    def get_cooked_bundles(self):
        """
        Get the cooked bundles
        """
        request = get_top_request(self.request)  # might be a subrequest

        # theme specific set bundles
        enabled_bundles = set(self.theme_enabled_bundles)
        disabled_bundles = set(self.theme_disabled_bundles)

        # Request set bundles
        enabled_bundles.update(getattr(request, 'enabled_bundles', []))
        disabled_bundles.update(getattr(request, 'disabled_bundles', []))

        for key, bundle in self.get_bundles().items():
            # The diazo manifest and request bundles are more important than
            # the disabled bundle on registry.
            # We can access the site with diazo.off=1 without diazo bundles
            if (
                key in disabled_bundles or
                (key not in enabled_bundles and not bundle.enabled) or
                not self.eval_expression(bundle.expression, bundle.name)
            ):
                continue

            yield key, bundle

    def ordered_bundles_result(self, production=False):
        """
        It gets the ordered result of bundles
        """
        result = []
        inserted = []
        depends_on = {}
        for key, bundle in self.get_cooked_bundles():
            if bundle.depends is None or bundle.depends == '':
                # its the first one
                if not(production and bundle.merge_with):
                    self.get_data(bundle, result)
                inserted.append(key)
            else:
                name = bundle.depends.strip()
                if name in depends_on:
                    depends_on[name].append(bundle)
                else:
                    depends_on[name] = [bundle]

        # We need to check all dependencies
        while len(depends_on) > 0:
            found = False
            for key, bundles_to_add in list(depends_on.items()):
                if key not in inserted:
                    continue
                found = True
                for bundle in bundles_to_add:
                    if not(production and bundle.merge_with):
                        self.get_data(bundle, result)
                    inserted.append(bundle.name)
                del depends_on[key]
            if not found:
                break

        # The ones that does not get the dependencies
        for bundles_to_add in depends_on.values():
            for bundle in bundles_to_add:
                if not(production and bundle.merge_with):
                    self.get_data(bundle, result)
        return result


class ResourceView(ResourceBase, ViewletBase):
    """Viewlet Information for script rendering.
    """
