# -*- coding: utf-8 -*-
from urlparse import urlparse
from urllib import quote

from Products.CMFPlone.resources.browser.cook import cookWhenChangingSettings
from Products.CMFPlone.resources.browser.resource import ResourceView


class StylesView(ResourceView):

    """ Information for style rendering. """

    def get_urls(self, style, bundle):
        """
        Extracts the urls for the specific resource
        """
        bundle_name = bundle.__prefix__.split(
            '/',
            1)[1].rstrip('.') if bundle else 'none'
        for css in style.css:
            url = urlparse(css)
            if url.netloc == '':
                # Local
                src = "%s/%s" % (self.site_url, css)
            else:
                src = "%s" % (css)

            extension = url.path.split('.')[-1]
            rel = 'stylesheet'
            if extension != '' and extension != 'css':
                rel = "stylesheet/%s" % extension

            data = {
                'rel': rel,
                'bundle': bundle_name,
                'conditionalcomment': bundle.conditionalcomment if bundle else '',  # noqa
                'src': src}
            yield data

    def get_data(self, bundle, result):
        """
        Gets the needed information for the bundle
        and stores it on the result list
        """
        bundle_name = bundle.__prefix__.split(
            '/',
            1)[1].rstrip('.') if bundle else 'none'
        if self.develop_bundle(bundle, 'develop_css'):
            self.resources = self.get_resources()
            # The bundle resources
            for resource in bundle.resources:
                if resource in self.resources:
                    style = self.resources[resource]
                    for data in self.get_urls(style, bundle):
                        result.append(data)
        else:
            if bundle.compile is False:
                # Its a legacy css bundle
                if not bundle.last_compilation\
                        or self.last_legacy_import > bundle.last_compilation:
                    # We need to compile
                    cookWhenChangingSettings(self.context, bundle)

            if bundle.csscompilation:
                css_path = bundle.csscompilation
                if '++plone++' in css_path:
                    resource_path = css_path.split('++plone++')[-1]
                    resource_name, resource_filepath = resource_path.split(
                        '/', 1)
                    css_location = '%s/++plone++%s/++unique++%s/%s' % (
                        self.site_url,
                        resource_name,
                        quote(str(bundle.last_compilation)),
                        resource_filepath
                    )
                else:
                    css_location = '%s/%s?version=%s' % (
                        self.site_url,
                        bundle.csscompilation,
                        quote(str(bundle.last_compilation))
                    )
                result.append({
                    'bundle': bundle_name,
                    'rel': 'stylesheet',
                    'conditionalcomment': bundle.conditionalcomment,
                    'src': css_location
                })

    def styles(self):
        """
        Get all the styles
        """
        if self.development or not self.production_path:
            result = self.ordered_bundles_result()
        else:
            result = [{
                'src': '%s/++plone++%s' % (
                    self.site_url,
                    self.production_path + '/default.css'
                ),
                'conditionalcomment': None,
                'rel': 'stylesheet',
                'bundle': 'production'
            }, ]
            if not self.anonymous:
                result.append({
                    'src': '%s/++plone++%s' % (
                        self.site_url,
                        self.production_path + '/logged-in.css'
                    ),
                    'conditionalcomment': None,
                    'rel': 'stylesheet',
                    'bundle': 'production'
                })
            result.extend(self.ordered_bundles_result(production=True))

        # Add manual added resources
        resources = self.get_resources()
        if hasattr(self.request, 'enabled_resources'):
            for resource in self.request.enabled_resources:
                if resource in resources:
                    for data in self.get_urls(resources[resource], None):
                        result.append(data)

        # Add diazo css
        origin = None
        if self.diazo_production_css and self.development is False:
            origin = self.diazo_production_css
        if self.diazo_development_css and self.development is True:
            origin = self.diazo_development_css
        if origin:
            url = urlparse(origin)
            if url.netloc == '':
                # Local
                src = "%s/%s" % (self.site_url, origin)
            else:
                src = "%s" % (origin)

            extension = url.path.split('.')[-1]
            rel = 'stylesheet'
            if extension != '' and extension != 'css':
                rel = "stylesheet/%s" % extension

            data = {'rel': rel,
                    'conditionalcomment': '',
                    'src': src,
                    'bundle': 'diazo'}

            result.append(data)
        return result
