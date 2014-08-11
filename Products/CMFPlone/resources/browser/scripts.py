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


class ScriptsView(ResourceView):
    """ Information for script rendering. """

    def get_data(self, bundle, result):
        resources = self.get_resources()
        if bundle.resource in resources:        
            script = resources[bundle.resource]
            url = urlparse(script.js)
            if url.netloc == '':
                # Local
                src = "%s/%s" % (self.portal_url, script.js)
            else:
                src = "%s" % (script.js)

            data = {'conditionalcomment' : bundle.conditionalcomment,
                    'src': src}
            result.append(data)

    def scripts(self):
        result = []
        if self.development():
            # We need to add require.js and config.js
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
