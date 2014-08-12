from Acquisition import aq_inner
from Products.PythonScripts.standard import url_quote
from Products.Five.browser import BrowserView
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.resources.interfaces import IBundleRegistry
from Products.CMFPlone.resources.browser.resource import ResourceView
from urlparse import urlparse
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import createExprContext


lessconfig = """
 window.less = {
    env: "development",
    logLevel: 2,
    async: false,
    fileAsync: false,
    errorReporting: 'console',
    poll: 1000,
    functions: {},
    dumpLineNumbers: "comments",
    globalVars: {
      %s
    },
  };
"""


class ScriptsView(ResourceView):
    """ Information for script rendering. """

    def get_data(self, bundle, result):
        resources = self.get_resources()
        if bundle.resource in resources:        
            script = resources[bundle.resource]
            if script.js:
                url = urlparse(script.js)
                if url.netloc == '':
                    # Local
                    src = "%s/%s" % (self.portal_url, script.js)
                else:
                    src = "%s" % (script.js)

                data = {'conditionalcomment' : bundle.conditionalcomment,
                        'src': src}
                result.append(data)

    def lessvariables(self):
        registryUtility = getUtility(IRegistry)
        return registryUtility.records['Products.CMFPlone.lessvariables'].value


    def less_config(self):
        registry = self.lessvariables()
        result = ""
        result += "sitePath: '%s',\n" % self.portal_url
        result += "isPlone: true,\n"

        for name, value in registry.items():
            result += "'%s': '\"%s\"',\n" % (name, value)

        for name, value in self.get_resources().items():
            for css in value.css:
                url = urlparse(css)
                if url.netloc == '':
                    # Local
                    src = "%s/%s" % (self.portal_url, css)
                else:
                    src = "%s" % (css)
                result += "'%s': '\"%s\"',\n" % (name, src)

        return lessconfig % result


    def scripts(self):
        """ 
        The requirejs scripts, the ones that are not resources
        are loaded on configjs.py
        """
        result = []
        if self.development():
            # We need to add require.js and config.js
            result.append({
                'src':'%s/%s' % (
                    self.portal_url, 
                    self.registry.records['Products.CMFPlone.resources.less-variables'].value)
                ,

                'conditionalcomment': None
            })
            result.append({
                'src':'%s/%s' % (
                    self.portal_url, 
                    self.registry.records['Products.CMFPlone.resources.lessc'].value)
                ,

                'conditionalcomment': None
            })
            result.append({
                'src':'%s/%s' % (
                    self.portal_url, 
                    self.registry.records['Products.CMFPlone.resources.requirejs'].value)
                ,

                'conditionalcomment': None
            })
            result.append({
                'src':'%s/%s' % (
                    self.portal_url, 
                    self.registry.records['Products.CMFPlone.resources.configjs'].value)
                ,
                'conditionalcomment': None
            })
        result.extend(self.ordered_result())
        return result
