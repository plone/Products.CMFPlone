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

    def get_bbb_styles(self):
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

    def get_config(self, style):
        """
        Gets the information of a specific style
        """
        data = None
        if style.enabled:
            if style.expression:
                    if style.cooked_expression:
                        expr = Expression(style.expression)
                        style.cooked_expression = expr
                    if self.evaluateExpression(style.cooked_expression, context):
                        return data
            url = urlparse(style.url)
            if url.netloc == '':
                # Local
                src = "%s/%s" % (self.portal_url, style.url)
            else:
                src = "%s" % (style.url)

            extension = url.path.split('.')[-1]
            rel = 'stylesheet'
            if extension != '' and extension != 'css':
                rel = "stylesheet/%s" % extension

            data = {'rel': rel,
                    'conditionalcomment' : style.conditionalcomment if bundle else '',
                    'src': src}
            return data


    def styles(self):
        """
        Get all the styles
        """
        # result = []
        result =  self.ordered_result()

        # Manual scripts
        registryUtility = getUtility(IRegistry)
        # Load the ordered list of js
        list_of_css = registryUtility.records['Products.CMFPlone.csslist']
        styles = self.get_bbb_styles()
        loaded = []
        for style_id in list_of_css.value:
            if style_id in styles:
                loaded.append(style_id)
                data = self.get_config(styles[style_id])
                if data:
                    result.append(data)

        # The rest of scripts
        for key, style in styles.items():
            if key not in loaded:
                data = self.get_config(style)
                if data:
                    result.append(data)
        return result



