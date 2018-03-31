# -*- coding: utf-8 -*-
from Products.CMFPlone.resources.browser.cook import cookWhenChangingSettings
from Products.CMFPlone.resources.browser.resource import ResourceView
from Products.CMFPlone.utils import get_top_request
from six.moves.urllib import parse
from zope.component import getMultiAdapter


class ScriptsView(ResourceView):
    """Information for script rendering.
    """

    def _add_resources(
        self,
        resources_to_add,
        result,
        bundle_name='none',
        resetrjs=False,
        conditionalcomment=''
    ):
        resources = self.get_resources()
        for resource in resources_to_add:
            data = resources.get(resource, None)
            if data is None or not data.js:
                continue
            url = parse.urlparse(data.js)
            if url.netloc == '':
                # Local
                src = '{0}/{1}'.format(self.site_url, data.js)
            else:
                src = data.js
            data = {
                'bundle': bundle_name,
                'conditionalcomment': conditionalcomment,
                'src': src,
                # Reset RequireJS if bundle is in non-compile to
                # avoid "Mismatched anonymous define()" in legacy
                # scripts.
                'resetrjs': resetrjs,
            }
            result.append(data)

    def get_data(self, bundle, result):
        if self.develop_bundle(bundle, 'develop_javascript'):
            # Bundle development mode
            self._add_resources(
                bundle.resources,
                result,
                bundle_name=bundle.name,
                resetrjs=bundle.compile is False,
                conditionalcomment=bundle.conditionalcomment,
            )
            return
        if (
            not bundle.compile and
            (
                not bundle.last_compilation or
                self.last_legacy_import > bundle.last_compilation
            ) and
            bundle.resources
        ):
            # Its a legacy bundle OR compiling is happening outside of plone

            # We need to combine files. It's possible no resources are
            # defined because the compiling is done outside of plone
            cookWhenChangingSettings(self.context, bundle)
        if bundle.jscompilation:
            js_path = bundle.jscompilation
            if '++plone++' in js_path:
                resource_path = js_path.split('++plone++')[-1]
                resource_name, resource_filepath = resource_path.split(
                    '/', 1)
                js_location = '{0}/++plone++{1}/++unique++{2}/{3}'.format(
                    self.site_url,
                    resource_name,
                    parse.quote(str(bundle.last_compilation)),
                    resource_filepath
                )
            else:
                js_location = '{0}/{1}?version={2}'.format(
                    self.site_url,
                    bundle.jscompilation,
                    parse.quote(str(bundle.last_compilation))
                )
            result.append({
                'bundle': bundle.name,
                'conditionalcomment': bundle.conditionalcomment,
                'src': js_location
            })

    def default_resources(self):
        """ Default resources used by Plone itself
        """
        result = []
        # We always add jquery resource
        result.append({
            'src': '{0}/{1}'.format(
                self.site_url,
                self.registry.records['plone.resources/jquery.js'].value),
            'conditionalcomment': None,
            'bundle': 'basic'
        })
        if self.development:
            # We need to add require.js and config.js
            result.append({
                'src': '{0}/{1}'.format(
                    self.site_url,
                    self.registry.records['plone.resources.less-variables'].value),  # noqa
                'conditionalcomment': None,
                'bundle': 'basic'
            })
            result.append({
                'src': '{0}/{1}'.format(
                    self.site_url,
                    self.registry.records['plone.resources.lessc'].value),
                'conditionalcomment': None,
                'bundle': 'basic'
            })
        result.append({
            'src': '{0}/{1}'.format(
                self.site_url,
                self.registry.records['plone.resources.requirejs'].value),
            'conditionalcomment': None,
            'bundle': 'basic'
        })
        result.append({
            'src': '{0}/{1}'.format(
                self.site_url,
                self.registry.records['plone.resources.configjs'].value),
            'conditionalcomment': None,
            'bundle': 'basic'
        })
        return result

    def base_url(self):
        portal_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state'
        )
        site_url = portal_state.portal_url()
        return site_url

    def scripts(self):
        """The requirejs scripts, the ones that are not resources are loaded on
        configjs.py
        """
        return self.default_resources()
        if self.debug_mode or self.development or not self.production_path:
            result = self.default_resources()
            result.extend(self.ordered_bundles_result())
        else:
            result = [{
                'src': '{0}/++plone++{1}'.format(
                    self.site_url,
                    self.production_path + '/default.js'
                ),
                'conditionalcomment': None,
                'bundle': 'production'
            }, ]
            if not self.anonymous:
                result.append({
                    'src': '{0}/++plone++{1}'.format(
                        self.site_url,
                        self.production_path + '/logged-in.js'
                    ),
                    'conditionalcomment': None,
                    'bundle': 'production'
                })
            result.extend(self.ordered_bundles_result(production=True))

        # Add manual added resources
        request = get_top_request(self.request)  # might be a subrequest
        enabled_resources = getattr(request, 'enabled_resources', [])
        if enabled_resources:
            self._add_resources(enabled_resources, result)

        # Add diazo url
        origin = None
        if self.diazo_production_js and not self.development:
            origin = self.diazo_production_js
        if self.diazo_development_js and self.development:
            origin = self.diazo_development_js
        if origin:
            result.append({
                'bundle': 'diazo',
                'conditionalcomment': '',
                'src': '{0}/{1}'.format(self.site_url, origin),
            })

        return result
