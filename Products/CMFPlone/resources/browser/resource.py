from Acquisition import aq_inner, aq_base, aq_parent
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IBundleRegistry
from Products.CMFPlone.interfaces import IResourceRegistry
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.theming.utils import theming_policy
from plone.registry.interfaces import IRegistry
from zope import component
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.ramcache.interfaces import ram
from Products.CMFCore.utils import _getAuthenticatedUser
from plone.memoize.view import memoize
from Products.CMFPlone.resources import RESOURCE_DEVELOPMENT_MODE


class ResourceView(ViewletBase):
    """Information for script rendering.
    """

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
        if _getAuthenticatedUser(self.context).getUserName() == 'Anonymous User':
            return False
        return self.registry.records['plone.resources.development'].value

    def develop_bundle(self, bundle, attr):
        if RESOURCE_DEVELOPMENT_MODE:
            return True
        return self.development and getattr(bundle, attr, False)

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
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.site_url = self.portal_state.portal_url()
        self.registry = getUtility(IRegistry)

    def get_bundles(self):
        return self.registry.collectionOfInterface(
            IBundleRegistry, prefix="plone.bundles", check=False)

    def get_resources(self):
        return self.registry.collectionOfInterface(
            IResourceRegistry, prefix="plone.resources", check=False)

    def get_cooked_bundles(self):
        """
        Get the cooked bundles
        """
        cache = component.queryUtility(ram.IRAMCache)
        bundles = self.get_bundles()
        policy = theming_policy(self.request)

        enabled_diazo_bundles = []
        disabled_diazo_bundles = []
        self.diazo_production_css = None
        self.diazo_development_css = None
        self.diazo_development_js = None
        self.diazo_production_js = None

        # Check if its Diazo enabled
        if policy.isThemeEnabled():
            themeObj = policy.get_theme()
            if themeObj:
                enabled_diazo_bundles = themeObj.enabled_bundles
                disabled_diazo_bundles = themeObj.disabled_bundles
                if hasattr(themeObj, 'production_css'):
                    self.diazo_production_css = themeObj.production_css
                    self.diazo_development_css = themeObj.development_css
                    self.diazo_development_js = themeObj.development_js
                    self.diazo_production_js = themeObj.production_js

        # Request set bundles
        enabled_request_bundles = []
        disabled_request_bundles = []
        if hasattr(self.request, 'enabled_bundles'):
            enabled_request_bundles.extend(self.request.enabled_bundles)

        if hasattr(self.request, 'disabled_bundles'):
            disabled_request_bundles.extend(self.request.disabled_bundles)

        for key, bundle in bundles.items():
            # The diazo manifest and request bundles are more important than
            # the disabled bundle on registry.
            # We can access the site with diazo.off=1 without diazo bundles
            if (bundle.enabled
                    or key in enabled_request_bundles
                    or key in enabled_diazo_bundles) and\
                    (key not in disabled_diazo_bundles
                        and key not in disabled_request_bundles):
                # check expression
                if bundle.expression:
                    cooked_expression = None
                    if cache is not None:
                        cooked_expression = cache.query(
                            'plone.bundles.cooked_expressions',
                            key=dict(prefix=bundle.__prefix__), default=None)
                    if (
                            cooked_expression is None or
                            cooked_expression.text != bundle.expression):
                        cooked_expression = Expression(bundle.expression)
                        if cache is not None:
                            cache.set(
                                cooked_expression,
                                'plone.bundles.cooked_expressions',
                                key=dict(prefix=bundle.__prefix__))
                    if not self.evaluateExpression(
                            cooked_expression, self.context):
                        continue
                yield key, bundle

    def ordered_bundles_result(self):
        """
        It gets the ordered result of bundles
        """
        result = []
        # The first one
        inserted = []
        depends_on = {}
        for key, bundle in self.get_cooked_bundles():
            if bundle.depends is None or bundle.depends == '':
                # its the first one
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
            for key, bundles_to_add in depends_on.items():
                if key in inserted:
                    found = True
                    for bundle in bundles_to_add:
                        self.get_data(bundle, result)
                        inserted.append(
                            bundle.__prefix__.split('/', 1)[1].rstrip('.'))
                    del depends_on[key]
            if not found:
                break

        # THe ones that does not get the dependencies
        for bundles_to_add in depends_on.values():
            for bundle in bundles_to_add:
                self.get_data(bundle, result)

        return result
