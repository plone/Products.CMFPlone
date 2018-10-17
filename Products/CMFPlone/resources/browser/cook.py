# -*- coding: utf-8 -*-
from datetime import datetime
from io import BytesIO
from plone.protect.interfaces import IDisableCSRFProtection
from plone.registry.interfaces import IRegistry
from plone.resource.interfaces import IResourceDirectory
from plone.subrequest import subrequest
from Products.CMFPlone.interfaces.resources import IBundleRegistry
from Products.CMFPlone.interfaces.resources import IResourceRegistry
from Products.CMFPlone.interfaces.resources import OVERRIDE_RESOURCE_DIRECTORY_NAME  # noqa
from Products.CMFPlone.resources.browser.combine import combine_bundles
from scss import Compiler
from slimit import minify
from zExceptions import NotFound
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.interface import alsoProvides

import logging
import six


logger = logging.getLogger('Products.CMFPlone')

REQUIREJS_RESET_PREFIX = """
/* reset requirejs definitions so that people who
   put requirejs in legacy compilation do not get errors */
var _old_define = define;
var _old_require = require;
define = undefined;
require = undefined;
try{
"""
REQUIREJS_RESET_POSTFIX = """
}catch(e){
    // log it
    if (typeof console !== "undefined"){
        console.log('Error loading javascripts!' + e);
    }
}finally{
    define = _old_define;
    require = _old_require;
}
"""


def cookWhenChangingSettings(context, bundle=None):
    """When our settings are changed, re-cook the not compilable bundles
    """
    registry = getUtility(IRegistry)
    resources = registry.collectionOfInterface(
        IResourceRegistry, prefix="plone.resources", check=False)
    if bundle is None:
        # default to cooking legacy bundle
        bundles = registry.collectionOfInterface(
            IBundleRegistry, prefix="plone.bundles", check=False)
        if 'plone-legacy' in bundles:
            bundle = bundles['plone-legacy']
        else:
            bundle = bundles.setdefault('plone-legacy')
            bundle.resources = []

    if not bundle.resources:
        # you can have a bundle without any resources defined and it's just
        # shipped as a legacy compiled js file
        return

    js_path = bundle.jscompilation
    css_path = bundle.csscompilation

    if not js_path and not css_path:
        logger.warn(
            'No js_path or css_path found. We need a plone.resource '
            'based resource path in order to store the compiled JS and CSS.'
        )
        return

    # Let's join all css and js
    css_compiler = Compiler(output_style='compressed')
    cooked_css = u''
    cooked_js = REQUIREJS_RESET_PREFIX
    siteUrl = getSite().absolute_url()
    request = getRequest()
    for package in bundle.resources or []:
        if package not in resources:
            continue
        resource = resources[package]

        if css_path:
            for css_resource in resource.css:
                css_url = siteUrl + '/' + css_resource
                response = subrequest(css_url)
                if response.status == 200:
                    logger.info('Cooking css %s', css_resource)
                    css = response.getBody()
                    if css_resource[-8:] != '.min.css':
                        css = css_compiler.compile_string(css)
                    if not isinstance(css, six.text_type):
                        css = css.decode('utf8')
                    cooked_css += u'\n/* Resource: {0} */\n{1}\n'.format(
                        css_resource,
                        css
                    )
                else:
                    cooked_css +=\
                        u'\n/* Could not find resource: {0} */\n\n'.format(
                            css_resource
                        )
                    logger.warn('Could not find resource: %s', css_resource)
        if not resource.js or not js_path:
            continue
        js_url = siteUrl + '/' + resource.js
        response = subrequest(js_url)
        if response.status == 200:
            js = response.getBody()
            try:
                logger.info('Cooking js %s', resource.js)
                if not isinstance(js, six.text_type):
                    js = js.decode('utf8')
                cooked_js += '\n/* resource: {0} */\n{1}'.format(
                    resource.js,
                    js if '.min.js' == resource.js[-7:] else
                    minify(js, mangle=False, mangle_toplevel=False)
                )
            except SyntaxError:
                cooked_js +=\
                    '\n/* Resource (error cooking): {0} */\n{1}'.format(
                        resource.js,
                        js
                    )
                logger.warn('Error cooking resource: %s', resource.js)
        else:
            logger.warn('Could not find resource: %s', resource.js)
            cooked_js += '\n/* Could not find resource: {0} */\n\n'.format(
                js_url
            )

    cooked_js += REQUIREJS_RESET_POSTFIX

    persistent_directory = getUtility(IResourceDirectory, name="persistent")
    if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
        persistent_directory.makeDirectory(OVERRIDE_RESOURCE_DIRECTORY_NAME)
    container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]

    def _write_resource(resource_path, cooked_string):
        if not resource_path:
            return
        resource_path = resource_path.split('++plone++')[-1]
        resource_name, resource_filepath = resource_path.split('/', 1)
        if resource_name not in container:
            container.makeDirectory(resource_name)
        if not isinstance(cooked_string, six.binary_type):  # handle Error of OFS.Image  # noqa: E501
            cooked_string = cooked_string.encode('ascii', errors='ignore')
        try:
            folder = container[resource_name]
            fi = BytesIO(cooked_string)
            folder.writeFile(resource_filepath, fi)
            logger.info('Writing cooked resource: %s', resource_path)
        except NotFound:
            logger.warn('Error writing cooked resource: %s', resource_path)

    _write_resource(js_path, cooked_js)
    _write_resource(css_path, cooked_css)

    bundle.last_compilation = datetime.now()
    # refresh production meta bundles
    combine_bundles(context)

    # Disable CSRF protection on this request
    alsoProvides(request, IDisableCSRFProtection)
