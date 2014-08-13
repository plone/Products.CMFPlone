from Acquisition import aq_inner
from Products.PythonScripts.standard import url_quote
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.resources.interfaces import IBundleRegistry, IResourceRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from Products.CMFPlone.resources.browser.configjs import ConfigJsView

from urlparse import urlparse
import re

optimize = """requirejs.optimize({
    baseUrl: '%s',
    paths: %s,
    shims: %s,
    optimize: "none",
    include: %s,
    out: function (text) {
        document.getElementById('%s').value = text;
    }
}, function (buildText) {
    document.getElementById('%s-debug').value = buildText;
});
"""


class OptimizeLESS(ConfigJsView):

    def get_bundles(self):
        bundles = self.registry.collectionOfInterface(IBundleRegistry, prefix="Products.CMFPlone.bundles")
        mains = []
        for key, bundle in bundles.items():
            mains.append(key)
        return mains


    def optimize(self):
        (baseUrl, paths, shims) = self.get_config()
        bundles = self.get_bundles()
        result = ""
        for bundle in bundles:
            result += optimize % (baseUrl, paths, shims, bundle, bundle)
        return result


class SaveOptimalLESS(BrowserView):

    def __call__(self):
        # We need to check auth, valid js
        # TODO
        if self.request.get('text', None):
            # Save the file on the resource directory .. registry ...
            pass