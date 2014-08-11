from Acquisition import aq_inner
from Products.PythonScripts.standard import url_quote
from Products.Five.browser import BrowserView
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.resources.interfaces import IBundleRegistry, IResourceRegistry
from plone.app.layout.viewlets.common import ViewletBase
from urlparse import urlparse
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import createExprContext
from zope.component import getMultiAdapter



class ResourceView(ViewletBase):
    """ Information for script rendering. """

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
        return self.registry.collectionOfInterface(IBundleRegistry, prefix="Products.CMFPlone.bundles")

    def get_resources(self):
        return self.registry.collectionOfInterface(IResourceRegistry, prefix="Products.CMFPlone.resources")

    def development(self):
        return self.registry.records['Products.CMFPlone.resources.development']

    def bundles(self):
        bundles = self.get_bundles()
        result = []
        for key, bundle in bundles.items():
            if bundle.enabled:
                # check expression
                if bundle.expression:
                    if bundle.cooked_expression:
                        expr = Expression(bundle.expression)
                        bundle.cooked_expression = expr
                    if self.evaluateExpression(bundle.cooked_expression, context):
                        continue
                yield key, bundle

    def ordered_result(self):
        missing_bundles = {}
        result = []
        # The first one
        inserted = []
        depends_on = {}
        for key, bundle in self.bundles():
            if bundle.depends is None or bundle.depends == '':
                # its the first one
                self.get_data(bundle, result)
                inserted.append(key)
            else: 
                for dependency in bundle.depends:
                    name = dependency.strip()
                    if name in depends_on:
                        depends_on[name].append(bundle)
                    else:
                        depends_on[name] = [bundle]

        while len(depends_on)>0:
            found = False
            for already_inserted in inserted:
                if already_inserted in depends_on:
                    found = True
                    for bundle in depends_on[already_inserted]:
                        self.get_data(bundle, result)
                        inserted.append(key)
                    del depends_on[already_inserted]
            if not found:
                continue

        for bundle in depends_on.values():
            self.get_data(bundle, result)

        return result