from Acquisition import aq_inner
from Products.PythonScripts.standard import url_quote
from Products.Five.browser import BrowserView
from Products.CMFPlone.resources.browser.resource import ResourceView
from urlparse import urlparse



class ScriptsView(ResourceView):
    """ Information for script rendering. """

    def get_data(self, bundle, result):
        if self.development is False:
            result.append({
                'conditionalcomment' : bundle.conditionalcomment,
                'src': '%s/%s?version=%s' % (self.portal_url, bundle.jscompilation, bundle.last_compilation)
                })
        else:
            resources = self.get_resources()
            # if bundle.compile:
            for resource in bundle.resources:
                if resource in resources:
                    script = resources[resource]
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
            # else:
            #     bundle_id = bundle.__prefix__.split('/')[1][:-1]
            #     src = "%s/not_compiled_js.js?bundle=%s" % (self.portal_url, bundle_id)
            #     data = {'conditionalcomment' : bundle.conditionalcomment,
            #             'src': src}
            #     result.append(data)

    def scripts(self):
        """ 
        The requirejs scripts, the ones that are not resources
        are loaded on configjs.py
        """
        result = []        
        # We always add jquery resource 
        result.append({
            'src':'%s/%s' % (
                self.portal_url, 
                self.registry.records['Products.CMFPlone.resources/jquery.js'].value)
            ,
            'conditionalcomment': None
        })


        if self.development:
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
            
        result.extend(self.ordered_bundles_result())

        return result
