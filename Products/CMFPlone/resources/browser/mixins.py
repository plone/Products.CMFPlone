# -*- coding: utf-8 -*-
from AccessControl.safe_formatter import SafeFormatter
from plone.registry.interfaces import IRegistry
from AccessControl.safe_formatter import SafeFormatter
from Products.CMFPlone.interfaces import IResourceRegistry
from Products.Five.browser import BrowserView
from urlparse import urlparse
from zope.component import getMultiAdapter
from zope.component import getUtility


lessconfig = """
 window.less = {
    env: "development",
    logLevel: %i,
    async: false,
    fileAsync: false,
    errorReporting: window.lessErrorReporting || 'console',
    poll: 1000,
    functions: {},
    relativeUrls: true,
    dumpLineNumbers: "comments",
    globalVars: {
      %s
    },
    modifyVars: {
      %s
    }
  };
"""

lessmodify = """
less.modifyVars({
    %s
})
"""


class LessConfiguration(BrowserView):
    """Browser view that gets the definition of less variables on plone.
    """

    def registry(self):
        registryUtility = getUtility(IRegistry)
        return registryUtility.records['plone.lessvariables'].value

    def resource_registry(self):
        registryUtility = getUtility(IRegistry)
        return registryUtility.collectionOfInterface(
            IResourceRegistry, prefix="plone.resources", check=False)

    def __call__(self):
        registry = self.registry()
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        site_url = portal_state.portal_url()
        result = ""
        result += "sitePath: '\"%s\"',\n" % site_url
        result += "isPlone: true,\n"
        result += "isMockup: false,\n"
        result += "staticPath: '\"%s/++plone++static\"',\n" % site_url
        result += "barcelonetaPath: '\"%s/++theme++barceloneta\"',\n" % site_url

        less_vars_params = {
            'site_url': site_url,
        }

        # Storing variables to use them on further vars
        for name, value in registry.items():
            less_vars_params[name] = value

        for name, value in registry.items():
            t = SafeFormatter(value).safe_format(**less_vars_params)
            result += "'%s': \"%s\",\n" % (name, t)

        # Adding all plone.resource entries css values as less vars
        for name, value in self.resource_registry().items():
            for css in value.css:

                url = urlparse(css)
                if url.netloc == '':
                    # Local
                    src = "%s/%s" % (site_url, css)
                else:
                    src = "%s" % (css)
                # less vars can't have dots on it
                result += "'%s': '\"%s\"',\n" % (name.replace('.', '_'), src)

        self.request.response.setHeader("Content-Type",
                                        "application/javascript")

        try:
            debug_level = int(self.request.get('debug', 2))
        except:
            debug_level = 2
        return lessconfig % (debug_level, result, result)


class LessModifyConfiguration(LessConfiguration):

    def __call__(self):
        registry = self.registry()
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        site_url = portal_state.portal_url()
        result2 = ""
        result2 += "'@sitePath': '\"%s\"',\n" % site_url
        result2 += "'@isPlone': true,\n"
        result2 += "'@isMockup': false,\n"
        result2 += "'@staticPath: '\"%s/++plone++static\"',\n" % site_url
        result2 += "'@barcelonetaPath: '\"%s/++theme++barceloneta\"',\n" % site_url

        less_vars_params = {
            'site_url': site_url,
        }

        # Storing variables to use them on further vars
        for name, value in registry.items():
            less_vars_params[name] = value

        for name, value in registry.items():
            t = SafeFormatter(value).safe_format(**less_vars_params)
            result2 += "'@%s': \"%s\",\n" % (name, t)

        self.request.response.setHeader("Content-Type",
                                        "application/javascript")

        return lessmodify % (result2)


class LessDependency(BrowserView):
    """Browser view that returns the less/css on less format for specific
    resource.
    """

    def registry(self):
        registryUtility = getUtility(IRegistry)
        return registryUtility.collectionOfInterface(
            IResourceRegistry, prefix="plone.resources", check=False)

    def __call__(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        site_url = portal_state.portal_url()

        registry = self.registry()
        resource = self.request.get('resource', None)
        result = ""
        if resource:
            if resource in registry:
                for css in registry[resource].css:
                    url = urlparse(css)
                    if url.netloc == '':
                        # Local
                        src = "%s/%s" % (site_url, css)
                    else:
                        src = "%s" % (css)

                    result += "@import url('%s');\n" % src

        self.request.response.setHeader("Content-Type", "stylesheet/less")

        return result
