from Products.Five.browser import BrowserView
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.resources.interfaces import IBundleRegistry, IResourceRegistry
from zope.component import getUtility
from zope.component import getMultiAdapter
from urlparse import urlparse

optimize = """
<!-- You need less.js Products.CMFPlone.resources.lessc on registry -->
    <link rel="stylesheet/less" type="text/css" href="http://localhost:8080/Plone/++plone++static/plone.less">
<!-- generates    <style type="text/css" id="less:Plone-plone-static-plone"> -->
"""


class OptimizeLESS(BrowserView):

    def get_bundles(self):
        registry = getUtility(IRegistry)
        bundles = registry.collectionOfInterface(IBundleRegistry, prefix="Products.CMFPlone.bundles")
        return bundles

    def get_resources(self):
        registry = getUtility(IRegistry)
        resources = registry.collectionOfInterface(IResourceRegistry, prefix="Products.CMFPlone.resources")
        return resources

    def __call__(self):
        """
        It gets the bundle name
        It returns the less file
        """
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        site_url = portal_state.portal_url()

        bundles = self.get_bundles()
        bundle = self.request.get('bundle', None)
        resources = self.get_resources()
        less_files = []
        if bundle and bundle in bundles:
            bundle_obj = bundles[bundle]
            for resource in bundle_obj.resources:
                if resource in resources:
                    for css in resources[resource]:
                        url = urlparse(css)
                        if url.netloc == '':
                            # Local
                            src = "%s/%s" % (site_url, css)
                        else:
                            src = "%s" % (css)

                        extension = url.path.split('.')[-1]
                        if extension == 'less':
                            less_files.append(src)
        return json.dumps({
            'less': less_files,
            })


