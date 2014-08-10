from Acquisition import aq_inner
from Products.PythonScripts.standard import url_quote
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
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
        return getToolByName(aq_inner(self.context), 'portal_javascripts')

    def skinname(self):
        return aq_inner(self.context).getCurrentSkinName()

    def get_config(self):
        registry = self.registry()
        registry_url = registry.absolute_url()
        base_url = registry_url
        context = aq_inner(self.context)
        skinname = url_quote(self.skinname())

        theme = registry.getCurrentSkinName()
        bundlesForThemes = registry.getBundlesForThemes()
        bundles = bundlesForThemes.get(theme, ['default'])
        if theme not in bundlesForThemes or theme not in registry.cookedResourcesByTheme:
            portal_skins = getToolByName(registry, 'portal_skins')
            theme = portal_skins.getDefaultSkin()

        results = [r.copy() for r in registry.getResources() \
                if r.getEnabled() and (not r.getBundle() or r.getBundle() in bundles)]

        scripts = [item for item in results if registry.evaluate(item, context)]

        # skinname = url_quote(self.skinname())
        paths = {}
        shims = {}
        mains = []
        norequire = []
        for script in scripts:
            requirejs = script.getComponent()
            if requirejs is '' and not bool(script.getDev()):
                norequire.append("%s/%s/%s" % (registry_url, skinname, script.getId()))
                continue

            inline = bool(script.getInline())

            if not inline and not script.isExternalResource() and requirejs != '':
                src = re.sub(r"\.js$", "", script.getId())
                paths[requirejs] = src
                exports = script.getExports()
                deps = script.getDeps()
                inits = script.getInit()
                main = script.getDataMain()
                if exports != '' or deps != '' or inits != '':
                    shims[requirejs] = {}
                    if exports != '':
                        shims[requirejs]['exports'] = exports
                    if deps != '':
                        shims[requirejs]['deps'] = deps.split(',')
                    if inits != '':
                        shims[requirejs]['init'] = script.getInit()
                if bool(main):
                    mains.append(script.getId())

        shims_str = str(shims).replace('\'deps\'', 'deps').replace('\'exports\'', 'exports').replace('\'init\': \'', 'init: ').replace('}\'}', '}}')
        return (base_url, str(paths), shims_str, str(mains), str(norequire))


class ConfigJsView(RequireJsView):
    """ config.js for requirejs for script rendering. """

    def __call__(self):
        (baseUrl, paths, shims, mains, norequire) = self.get_config()
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

    def __call__(self):
        (baseUrl, paths, shims, mains, norequire) = self.get_config()
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


class OptimizeJS(RequireJsView):

    def optimize(self):
        (baseUrl, paths, shims, mains, norequire) = self.get_config()
        return optimize % (baseUrl, paths, shims, mains)


class SaveOpimalJS(BrowserView):

    def __call__(self):
        # We need to check auth, valid js
        # TODO
        if self.request.get('text', None):
            # Save the file on the resource directory .. registry ...
            pass
