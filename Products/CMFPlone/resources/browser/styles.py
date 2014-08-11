from Acquisition import aq_inner
from Products.PythonScripts.standard import url_quote
from Products.Five.browser import BrowserView
from Products.CMFPlone.resources.browser.resource import ResourceView
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.resources.interfaces import IResourceRegistry
from Products.CMFPlone.resources.interfaces import IJSManualResource, ICSSManualResource
from urlparse import urlparse

from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import createExprContext




class StylesView(ResourceView):
    """ Information for style rendering. """

    def get_manual_resources(self):
        return self.registry.collectionOfInterface(ICSSManualResource, prefix="Products.CMFPlone.manualcss")

    def get_urls(self, style, bundle):
        for css in style.css:
            url = urlparse(css)
            if url.netloc == '':
                # Local
                src = "%s/%s" % (self.portal_url, css)
            else:
                src = "%s" % (css)

            extension = url.path.split('.')[-1]
            rel = 'stylesheet'
            if extension != '' and extension != 'css':
                rel = "stylesheet/%s" % extension

            data = {'rel': rel,
                    'conditionalcomment' : bundle.conditionalcomment if bundle else '',
                    'src': src}
            yield data

    def get_data(self, bundle, result):
        """ 
        Gets the needed information for the bundle
        and stores it on the result list
        """
        self.resources = self.get_resources()
        # The bundle resources
        if bundle.resource in self.resources:        
            style = self.resources[bundle.resource]
            for data in self.get_urls(style, bundle):
                result.append(data)
        # The forced resources

    def styles(self):
        """
        Get all the styles
        """
        # result = []
        result =  self.ordered_result()

        # Manual code
        for key, resource in self.get_manual_resources().items():
            if resource.enabled:
                if resource.expression:
                        if resource.cooked_expression:
                            expr = Expression(resource.expression)
                            resource.cooked_expression = expr
                        if self.evaluateExpression(resource.cooked_expression, context):
                            continue
                url = urlparse(resource.url)
                if url.netloc == '':
                    # Local
                    src = "%s/%s" % (self.portal_url, resource.url)
                else:
                    src = "%s" % (resource.url)

                extension = url.path.split('.')[-1]
                rel = 'stylesheet'
                if extension != '' and extension != 'css':
                    rel = "stylesheet/%s" % extension

                data = {'rel': rel,
                        'conditionalcomment' : resource.conditionalcomment if bundle else '',
                        'src': src}
                result.append(data)

        return result


