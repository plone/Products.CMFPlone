from Acquisition import aq_inner
from Products.PythonScripts.standard import url_quote
from Products.Five.browser import BrowserView
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.resources.interfaces import IResourceRegistry
from plone.app.layout.viewlets.common import ViewletBase
from urlparse import urlparse
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import createExprContext


class ScriptsView(ViewletBase):
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


    def registry(self):
        registry = getUtility(IRegistry)
        return registry.collectionOfInterface(IResourceRegistry, prefix="Products.CMFPlone.resources")

    def scripts(self):
        resources = self.registry()

        result = []
        for resource in resources:
            if script.js and script.bundle:
                # check expression
                if script.expression:
                    if script.cooked_expression:
                        expr = Expression(script.expression)
                        script.cooked_expression = expr
                    if self.evaluateExpression(script.cooked_expression, context):
                        continue
                url = urlparse(script.js)
                if url.netloc == '':
                    # Local
                    src = "%s/%s" % (self.portal_url, script.js)
                else:
                    src = "%s" % (script.js)

            data = {'conditionalcomment' : script.conditionalcomment,
                    'src': src}
            result.append(data)
        return result
