from .utils import get_resource
from webresource import ScriptResource
from webresource import StyleResource


class PloneBaseResource:
    """Mixin to override certain aspects of a webresource for Plone needs."""

    def __init__(self, context, **kw):
        """Initialize with Plone context"""
        self.context = context
        super().__init__(**kw)

    @property
    def file_data(self):
        """Fetch data from using a resource via traversal"""
        data = get_resource(self.context, self.resource)
        if isinstance(data, str):
            data = data.encode("utf8")
        return data


class PloneScriptResource(PloneBaseResource, ScriptResource):
    """Webresource based ScriptResource for Plone"""


class PloneStyleResource(PloneBaseResource, StyleResource):
    """Webresource based StyleResource for Plone"""