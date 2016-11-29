# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import IResourceRegistry
from Products.Five.browser import BrowserView
from zope.component import getUtility

import json
import re


configjs = """requirejs.config({
    baseUrl: PORTAL_URL,
    paths: %s,
    shim: %s,
    optimize: 'uglify',
    wrapShim: true
});"""


def _format_shims(shims):
    result = []
    for name, val in shims.items():
        options = []
        if val.get('exports'):
            options.append('exports: "%s"' % val['exports'])
        if val.get('deps'):
            options.append('deps: ' + json.dumps(val['deps']))
        if val.get('init'):
            # function, no escaping here
            options.append('init: %s' % val['init'])
        result.append("""
        "%s": {
            %s
        }""" % (name, ',\n            '.join(options)))
    return '{' + ','.join(result) + '\n    }'


class RequireJsView(BrowserView):
    """
    This view creates the config.js for requirejs with all the registered
    resources

    It's used on development for the config.js and on compilation for the
    optimize.js
    """

    @property
    def registry(self):
        return getUtility(IRegistry)

    def registryResources(self):
        return self.registry.collectionOfInterface(
            IResourceRegistry, prefix="plone.resources", check=False)

    def get_requirejs_config(self):
        """
        Returns the information for requirejs configuration
        """
        registry = self.registryResources()
        paths = {}
        shims = {}
        for name, script in registry.items():
            if script.js:
                # Main resource js file
                src = re.sub(r"\.js$", "", script.js)
                paths[name] = src
                exports = script.export
                deps = script.deps
                inits = script.init
                if exports or deps or inits:
                    shims[name] = {}
                    if exports not in ('', None):
                        shims[name]['exports'] = exports
                    if deps not in ('', None):
                        shims[name]['deps'] = deps.split(',')
                    if inits not in ('', None):
                        shims[name]['init'] = inits
            if script.url:
                # Resources available under name-url name
                src = script.url
                paths[name + '-url'] = src
        return (paths, shims)


class ConfigJsView(RequireJsView):
    """ config.js for requirejs for script rendering. """

    def __call__(self):
        (paths, shims) = self.get_requirejs_config()
        self.request.response.setHeader("Content-Type",
                                        "application/javascript")
        return configjs % (
            json.dumps(paths, indent=4),
            _format_shims(shims)
        )
