from Acquisition import aq_inner
from Products.PythonScripts.standard import url_quote
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.resources.interfaces import IBundleRegistry, IResourceRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility

from urlparse import urlparse
import re


configjs = """requirejs.config({
    baseUrl: '%s',
    paths: %s,
    shim: %s,
    optimize: 'uglify',
    wrapShim: true
});

"""


class RequireJsView(BrowserView):
    def registry(self):
        self.registry = getUtility(IRegistry)
        return self.registry.collectionOfInterface(IResourceRegistry, prefix="Products.CMFPlone.resources")

    def base_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                name=u'plone_portal_state')
        site_url = portal_state.portal_url()
        return site_url




class ConfigJsView(RequireJsView):
    """ config.js for requirejs for script rendering. """

    def get_config(self):
        registry = self.registry()

        paths = {}
        shims = {}
        mains = []
        norequire = []
        for requirejs, script in registry.items():
            if script.js:
                src = re.sub(r"\.js$", "", script.js)
                paths[requirejs] = src
                exports = script.exports
                deps = script.deps
                inits = script.init
                if exports != '' or deps != '' or inits != '':
                    shims[requirejs] = {}
                    if exports != '':
                        shims[requirejs]['exports'] = exports
                    if deps != '':
                        shims[requirejs]['deps'] = deps.split(',')
                    if inits != '':
                        shims[requirejs]['init'] = script.getInit()

        shims_str = str(shims).replace('\'deps\'', 'deps').replace('\'exports\'', 'exports').replace('\'init\': \'', 'init: ').replace('}\'}', '}}')
        return (self.base_url(), str(paths), shims_str)

    def __call__(self):
        (baseUrl, paths, shims) = self.get_config()
        self.request.response.setHeader("Content-Type", "application/javascript")
        return configjs % (baseUrl, paths, shims)


bbbplone = """require([
  'jquery',
  'bundle-plone'
], function($, Plone) {
  'use strict';

  require(%s, function(undefined){
    // initialize only if we are in top frame
    if (window.parent === window) {
      $(document).ready(function() {
        $('body').addClass('pat-bbbplone');
      });
    }
  })
});"""


class BBBConfigJsView(RequireJsView):
    """ bbbplone.js for non-requirejs code """

    def get_config(self):
        norequire = []
        registry = self.registry()
        for key, script in registry.items():
            if script.force:
                url = urlparse(script.js)
                if url.netloc == '':
                    # Local
                    src = "%s/%s" % (self.base_url(), script.js)
                else:
                    src = "%s" % (script.js)
                norequire.append(src)
                continue

    def __call__(self):
        norequire = self.get_config()
        self.request.response.setHeader("Content-Type", "application/javascript")
        return bbbplone % (norequire)


optimize = """requirejs.optimize({
    baseUrl: '%s',
    paths: %s,
    shims: %s,
    optimize: "none",
    include: %s,
    out: function (text) {
        document.getElementById('output').value = text;
    }
}, function (buildText) {
    document.getElementById('buildMessages').value = buildText;
});
"""


class OptimizeJS(ConfigJsView):

    def get_bundles(self):
        bundles = self.registry.collectionOfInterface(IBundleRegistry, prefix="Products.CMFPlone.bundles")
        mains = []
        for key, bundle in bundles.items():
            mains.append(key)
        return mains


    def optimize(self):
        (baseUrl, paths, shims) = self.get_config()
        mains = self.get_bundles()
        return optimize % (baseUrl, paths, shims, mains)


class SaveOpimalJS(BrowserView):

    def __call__(self):
        # We need to check auth, valid js
        # TODO
        if self.request.get('text', None):
            # Save the file on the resource directory .. registry ...
            pass
