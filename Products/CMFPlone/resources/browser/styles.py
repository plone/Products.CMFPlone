from Acquisition import aq_inner
from Products.PythonScripts.standard import url_quote
from Products.Five.browser import BrowserView
from Products.CMFPlone.resources.browser.resource import ResourceView
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.resources.interfaces import IResourceRegistry
from urlparse import urlparse

from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import createExprContext




class StylesView(ResourceView):
    """ Information for style rendering. """

    def get_urls(self, style, bundle):
        for css in style.css:
            url = urlparse(css)
            if url.netloc == '':
                # Local
                src = "%s/%s" % (self.portal_url, css)
            else:
                src = "%s" % (css)

            extension = url.path.split('.')[-1]
            if extension != '' and extension != 'css':
                src = "%s/@@compile_%s?url=%s" % (self.portal_url, extension, url_quote(src))

            data = {'rel': 'stylesheet',
                    'conditionalcomment' : bundle.conditionalcomment,
                    'src': src}
            yield data

    def get_css_deps(self, style, result, bundle):
        if style.css_deps:
            self.get_css_deps(style, result, bundle)
            for data in self.get_urls(style, bundle):
                result.append(data)
        else:
            for data in self.get_urls(style, bundle):
                result.append(data)            

    def get_data(self, bundle, result):
        resources = self.get_resources()
        if bundle.resource in resources:        
            style = resources[bundle.resource]
            self.get_css_deps(style, result, bundle)

    def styles(self):
        self.inserted_css = []
        return self.ordered_result()

