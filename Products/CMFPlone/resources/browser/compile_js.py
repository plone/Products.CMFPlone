from Acquisition import aq_inner
from Products.PythonScripts.standard import url_quote
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.resources.interfaces import IBundleRegistry, IResourceRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from Products.CMFPlone.resources.browser.configjs import RequireJsView

from urlparse import urlparse
import re

optimize = """
// YOU NEED r.js Products.CMFPlone.resources.rjs entry on the registry
document.getElementById('build-%s').addEventListener('click', function (evt) {

    requirejs.optimize({
        baseUrl: '.',
        paths: %s,
        shims: %s,
        include: %s,
        out: function (text) {
            document.getElementById('%s').value = text;
        }
    }, function (buildText) {
        document.getElementById('%s-debug').value = buildText;
    });
}, false);

"""


class OptimizeJS(RequireJsView):

    def get_bundles(self):
        bundles = self.registry.collectionOfInterface(IBundleRegistry, prefix="Products.CMFPlone.bundles")
        return bundles

    def __call__(self):
        """
        Returns the shims/paths/and include
        Gets a get parameter with the name of the bundle
        """
        (baseUrl, paths, shims) = self.get_requirejs_config()
        bundles = self.get_bundles()
        bundle = self.request.get('bundle', None)
        resources = []
        if bundle and bundle in bundles:
            bundle_obj = bundles[bundle]
            for resource in bundle_obj.resources:
                resources.append(resource)
        return json.dumps({
            'include': resources,
            'shims': shims,
            'paths': paths
            })

