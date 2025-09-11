from .utils import evaluateExpression
from .utils import get_resource
from Products.CMFCore.Expression import Expression
from webresource import ScriptResource
from webresource import StyleResource
from zope.component import queryUtility
from zope.ramcache.interfaces import ram


class PloneBaseResource:
    """Mixin to override certain aspects of a webresource for Plone needs."""

    def __init__(self, context, **kw):
        """Initialize with Plone context"""
        self.context = context
        self.expression = kw.pop("expression", "")
        super().__init__(**kw)

    @property
    def file_data(self):
        """Fetch data from using a resource via traversal"""
        data = get_resource(self.context, self.resource)
        if data is None:
            # This happens with plone.session when trying to get a resource
            # with this path:
            # "acl_users/session/refresh?session_refresh=true&type=css&minutes=5"
            # We could 'return b""', but let's take the resource path instead.
            data = self.resource
        if isinstance(data, str):
            data = data.encode("utf8")
        return data

    @property
    def include(self):
        if callable(self._include):
            # Note: at time of writing, this is not used in core Plone.
            # But upstream webresource has it, so let's keep it.
            return self._include()
        if not self._include:
            return False
        # We want to include the resource, but must evaluate the expression first.
        return self.eval_expression()

    @include.setter
    def include(self, include):
        self._include = include

    def eval_expression(self):
        if not self.expression:
            return True
        cache = queryUtility(ram.IRAMCache)
        cooked_expression = None
        if cache is not None:
            cooked_expression = cache.query(
                "plone.bundles.cooked_expressions",
                key=dict(prefix=self.name),
                default=None,
            )
        if cooked_expression is None or cooked_expression.text != self.expression:
            cooked_expression = Expression(self.expression)
            if cache is not None:
                cache.set(
                    cooked_expression,
                    "plone.bundles.cooked_expressions",
                    key=dict(prefix=self.name),
                )
        return evaluateExpression(cooked_expression, self.context)


class PloneScriptResource(PloneBaseResource, ScriptResource):
    """Webresource based ScriptResource for Plone"""


class PloneStyleResource(PloneBaseResource, StyleResource):
    """Webresource based StyleResource for Plone"""
