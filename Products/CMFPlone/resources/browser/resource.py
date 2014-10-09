from Acquisition import aq_inner, aq_base, aq_parent
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import (
    IBundleRegistry,
    IResourceRegistry)
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import createExprContext
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from plone.app.theming.utils import getCurrentTheme
from plone.app.theming.utils import isThemeEnabled
from plone.app.theming.utils import getTheme


class ResourceView(ViewletBase):
    """ Information for script rendering. """

    @property
    def development(self):
        return self.registry.records['plone.resources.development'].value

    @property
    def last_legacy_import(self):
        return self.registry.records['plone.resources.last_legacy_import'].value

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
            IBundleRegistry, prefix="plone.bundles")

    def get_resources(self):
        return self.registry.collectionOfInterface(
            IResourceRegistry, prefix="plone.resources")

    def get_cooked_bundles(self):
        """
        Get the cooked bundles
        """
        bundles = self.get_bundles()
        # Check if its Diazo enabled
        if isThemeEnabled(self.request):
            theme = getCurrentTheme()
            themeObj = getTheme(theme)
            enabled_diazo_bundles = themeObj.enabled_bundles
            disabled_diazo_bundles = themeObj.disabled_bundles
        else:
            enabled_diazo_bundles = []
            disabled_diazo_bundles = []
        for key, bundle in bundles.items():
            # The diazo manifest is more important than the disabled bundle on registry
            # We can access the site with diazo.off=1 without diazo bundles
            if (bundle.enabled or key in enabled_diazo_bundles) and (key not in disabled_diazo_bundles):
                # check expression
                if bundle.expression:
                    if bundle.cooked_expression:
                        expr = Expression(bundle.expression)
                        bundle.cooked_expression = expr
                    if self.evaluateExpression(bundle.cooked_expression,
                                               self.context):
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

        while len(depends_on) > 0:
            found = False
            for key, bundles_to_add in depends_on.items():
                if key in inserted:
                    found = True
                    for bundle in bundles_to_add:
                        self.get_data(bundle, result)
                        inserted.append(key)
                    del depends_on[key]
            if not found:
                continue

        # THe ones that does not get the dependencies
        for bundle in depends_on.values():
            self.get_data(bundle, result)

        return result

    # def get_manual_order(self, kind):
    #     resources = self.get_manual_resources(kind)
    #     to_order = resources.keys()
    #     result = []
    #     depends_on = {}
    #     for key, resource in resources.items():
    #         if resource.depends is not None or resource.depends != '':
    #             if resource.depends in depends_on:
    #                 depends_on[resource.depends].append(key)
    #             else:
    #                 depends_on[resource.depends] = [key]


    #     ordered = []
    #     depends = {}
    #     insert_point = 0
    #     # First the ones that are not depending or dependences are not here
    #     for key, resource in resources.items():
    #         if resource.depends is None or resource.depends == '':
    #             ordered.insert(0, key)
    #             insert_point += 1
    #         else:
    #             if resource.depends in to_order:
    #                 depends[key] = resource
    #             else:
    #                 ordered.insert(len(to_order), key)

    #     # The dependency ones
    #     while len(depends) > 0:
    #         to_remove = []
    #         for key in depends.keys():
    #             if resources[key].depends in ordered:
    #                 ordered.insert(ordered.index(resources[key].depends) + 1, key)  # noqa
    #                 to_remove.append(key)
    #         for e in to_remove:
    #             del depends[e]
    #         if len(to_remove) == 0:
    #             continue

    #     for key in to_order:
    #         data = self.get_manual_data(resources[key])
    #         if data:
    #             result.append(data)

    #     return result
