from Products.CMFPlone.resources.browser.resource import ResourceView
from Products.CMFPlone.resources.browser.cook import cookWhenChangingSettings
from urlparse import urlparse


class StylesView(ResourceView):
    """ Information for style rendering. """


    def get_urls(self, style, bundle):
        """
        Extracts the urls for the specific resource
        """
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
        if self.development is False:
            if bundle.compile is False:
                # Its a legacy css bundle
                self.resources = self.get_resources()
                # The bundle resources
                for resource in bundle.resources:
                    if resource in self.resources:        
                        style = self.resources[resource]
                        for data in self.get_urls(style, bundle):
                            result.append(data)
                # if not bundle.last_compilation or self.last_legacy_import > bundle.last_compilation:
                #     # We need to compile
                #     cookWhenChangingSettings(self.context, bundle)

            if bundle.csscompilation:
                result.append({
                    'rel': 'stylesheet',
                    'conditionalcomment' : bundle.conditionalcomment,
                    'src': '%s/%s?version=%s' % (self.portal_url, bundle.csscompilation, bundle.last_compilation)
                    })
        else:
            self.resources = self.get_resources()
            # The bundle resources
            for resource in bundle.resources:
                if resource in self.resources:        
                    style = self.resources[resource]
                    for data in self.get_urls(style, bundle):
                        result.append(data)

    # def get_manual_data(self, style):
    #     """
    #     Gets the information of a specific style
    #     Style is a CSS manual entry
    #     """
    #     data = None
    #     if style.enabled:
    #         if style.expression:
    #                 if style.cooked_expression:
    #                     expr = Expression(style.expression)
    #                     style.cooked_expression = expr
    #                 if self.evaluateExpression(style.cooked_expression, context):
    #                     return data
    #         url = urlparse(style.url)
    #         if url.netloc == '':
    #             # Local
    #             src = "%s/%s" % (self.portal_url, style.url)
    #         else:
    #             src = "%s" % (style.url)

    #         extension = url.path.split('.')[-1]
    #         rel = 'stylesheet'
    #         if extension != '' and extension != 'css':
    #             rel = "stylesheet/%s" % extension

    #         data = {'rel': rel,
    #                 'conditionalcomment' : style.conditionalcomment,
    #                 'src': src}
    #         return data


    def styles(self):
        """
        Get all the styles
        """
        result =  self.ordered_bundles_result()
        # manual_result = self.get_manual_order('css')
        # result.extend(manual_result)

        return result



