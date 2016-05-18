from urlparse import urlparse
from urllib import quote

from Products.CMFPlone.resources.browser.cook import cookWhenChangingSettings
from Products.CMFPlone.resources.browser.resource import ResourceView
from zope.component import getMultiAdapter


class ScriptsView(ResourceView):
    """Information for script rendering.
    """

    def get_data(self, bundle, result):
        bundle_name = bundle.__prefix__.split('/', 1)[1].rstrip('.')
        if self.develop_bundle(bundle, 'develop_javascript'):
            resources = self.get_resources()
            for resource in bundle.resources:
                if resource in resources:
                    script = resources[resource]
                    if script.js:
                        url = urlparse(script.js)
                        if url.netloc == '':
                            # Local
                            src = "%s/%s" % (self.site_url, script.js)
                        else:
                            src = "%s" % (script.js)

                        data = {
                            'bundle': bundle_name,
                            'conditionalcomment': bundle.conditionalcomment,  # noqa
                            'src': src}
                        result.append(data)
        else:
            if bundle.compile is False:
                # Its a legacy css bundle OR compiling is happening outside of
                # plone
                if ((not bundle.last_compilation
                        or self.last_legacy_import > bundle.last_compilation)
                        and bundle.resources):
                    # We need to combine files. It's possible no resources are defined
                    # because the compiling is done outside of plone
                    cookWhenChangingSettings(self.context, bundle)
            if bundle.jscompilation:
                js_path = bundle.jscompilation
                if '++plone++' in js_path:
                    resource_path = js_path.split('++plone++')[-1]
                    resource_name, resource_filepath = resource_path.split(
                        '/', 1)
                    js_location = '%s/++plone++%s/++unique++%s/%s' % (
                        self.site_url,
                        resource_name,
                        quote(str(bundle.last_compilation)),
                        resource_filepath
                    )
                else:
                    js_location = '%s/%s?version=%s' % (
                        self.site_url,
                        bundle.jscompilation,
                        quote(str(bundle.last_compilation))
                    )
                result.append({
                    'bundle': bundle_name,
                    'conditionalcomment': bundle.conditionalcomment,
                    'src': js_location
                })

    def default_resources(self):
        """ Default resources used by Plone itself
        """
        result = []
        # We always add jquery resource
        result.append({
            'src': '%s/%s' % (
                self.site_url,
                self.registry.records['plone.resources/jquery.js'].value),
            'conditionalcomment': None,
            'bundle': 'basic'
        })
        if self.development:
            # We need to add require.js and config.js
            result.append({
                'src': '%s/%s' % (
                    self.site_url,
                    self.registry.records['plone.resources.less-variables'].value),  # noqa
                'conditionalcomment': None,
                'bundle': 'basic'
            })
            result.append({
                'src': '%s/%s' % (
                    self.site_url,
                    self.registry.records['plone.resources.lessc'].value),
                'conditionalcomment': None,
                'bundle': 'basic'
            })
        result.append({
            'src': '%s/%s' % (
                self.site_url,
                self.registry.records['plone.resources.requirejs'].value),
            'conditionalcomment': None,
            'bundle': 'basic'
        })
        result.append({
            'src': '%s/%s' % (
                self.site_url,
                self.registry.records['plone.resources.configjs'].value),
            'conditionalcomment': None,
            'bundle': 'basic'
        })
        return result

    def base_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        site_url = portal_state.portal_url()
        return site_url

    def scripts(self):
        """The requirejs scripts, the ones that are not resources are loaded on
        configjs.py
        """
        if self.development or not self.production_path:
            result = self.default_resources()
            result.extend(self.ordered_bundles_result())
        else:
            result = [{
                'src': '%s/++plone++%s' % (
                    self.site_url,
                    self.production_path + '/default.js'
                ),
                'conditionalcomment': None,
                'bundle': 'production'
            }, ]
            if not self.anonymous:
                result.append({
                    'src': '%s/++plone++%s' % (
                        self.site_url,
                        self.production_path + '/logged-in.js'
                    ),
                    'conditionalcomment': None,
                    'bundle': 'production'
                })
            result.extend(self.ordered_bundles_result(production=True))

        # Add manual added resources
        if hasattr(self.request, 'enabled_resources'):
            resources = self.get_resources()
            for resource in self.request.enabled_resources:
                if resource in resources:
                    data = resources[resource]
                    if data.js:
                        url = urlparse(data.js)
                        if url.netloc == '':
                            # Local
                            src = "%s/%s" % (self.site_url, data.js)
                        else:
                            src = "%s" % (data.js)

                        data = {
                            'bundle': 'none',
                            'conditionalcomment': '',  # noqa
                            'src': src}
                        result.append(data)

        # Add diazo url
        origin = None
        if self.diazo_production_js and self.development is False:
            origin = self.diazo_production_js
        if self.diazo_development_js and self.development is True:
            origin = self.diazo_development_js
        if origin:
            result.append({
                'bundle': 'diazo',
                'conditionalcomment': '',
                'src': '%s/%s' % (
                    self.site_url, origin)
            })

        return result
