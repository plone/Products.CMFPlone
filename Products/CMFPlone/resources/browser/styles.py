# -*- coding: utf-8 -*-
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFPlone.resources.browser.cook import cookWhenChangingSettings
from Products.CMFPlone.resources.browser.resource import ResourceBase
from Products.CMFPlone.utils import get_top_request
from six.moves.urllib import parse

import six


class StylesBase(ResourceBase):

    """ Information for style rendering. """

    def get_urls(self, style, bundle):
        """
        Extracts the urls for the specific resource
        """
        for css in style.css:
            url = parse.urlparse(css)
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
                'bundle': bundle.name if bundle else 'none',
                'conditionalcomment':
                    bundle.conditionalcomment if bundle else '',
                'src': src}
            yield data

    def get_data(self, bundle, result):
        """
        Gets the needed information for the bundle
        and stores it on the result list
        """
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
                        parse.quote(str(bundle.last_compilation)),
                        resource_filepath
                    )
                else:
                    css_location = '%s/%s?version=%s' % (
                        self.site_url,
                        bundle.csscompilation,
                        parse.quote(str(bundle.last_compilation))
                    )
                result.append({
                    'bundle': bundle.name,
                    'rel': 'stylesheet',
                    'conditionalcomment': bundle.conditionalcomment,
                    'src': css_location
                })

    def styles(self):
        """
        Get all the styles
        """
        if six.PY3:
            return
        if self.development or self.debug_mode or not self.production_path:
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
        request = get_top_request(self.request)  # might be a subrequest
        if hasattr(request, 'enabled_resources'):
            for resource in request.enabled_resources:
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
            url = parse.urlparse(origin)
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


class StylesView(StylesBase, ViewletBase):
    """Styles Viewlet
    """
