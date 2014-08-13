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

    def get_manual_data(self, style):
        """
        Gets the information of a specific style
        Style is a CSS manual entry
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
                    'conditionalcomment' : style.conditionalcomment,
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
        styles = self.get_bbb_styles()
        to_order = styles.keys()
        # Quick Sort
        depends_on = {}
        for key, style in styles.items():
            if style.depends is not None or style.depends != '':
                if style.depends in depends_on:
                    depends_on[style.depends].append(key)
                else:
                    depends_on[style.depends] = [key]


        ordered = []
        depends = {}
        insert_point = 0
        # First the ones that are not depending or dependences are not here
        for key, style in styles.items():
            if style.depends is None or style.depends == '':
                ordered.insert(0, key)
                insert_point += 1
            else:
                if style.depends in to_order:
                    depends[key] = style
                else:
                    ordered.insert(len(to_order), key)

        # The dependency ones
        while len(depends) > 0:
            to_remove = []
            for key in depends.keys():
                if style.depends in ordered:
                    ordered.insert(ordered.index(style.depends) + 1, key)
                    to_remove.append(key)
            for e in to_remove:
                del depends[e]

        for key in to_order:
            data = self.get_manual_data(styles[key])
            if data:
                result.append(data)


        return result



