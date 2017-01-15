# -*- coding: utf-8 -*-
from cssmin import cssmin
from datetime import datetime
from plone.protect.interfaces import IDisableCSRFProtection
from plone.registry.interfaces import IRegistry
from plone.resource.interfaces import IResourceDirectory
from plone.subrequest import subrequest
from Products.CMFPlone.interfaces.resources import IBundleRegistry
from Products.CMFPlone.interfaces.resources import IResourceRegistry
from Products.CMFPlone.interfaces.resources import OVERRIDE_RESOURCE_DIRECTORY_NAME  # noqa
from Products.CMFPlone.resources.browser.combine import combine_bundles
from slimit import minify
from StringIO import StringIO
from zExceptions import NotFound
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.interface import alsoProvides

import logging


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

    # Let's join all css and js
    cooked_css = ''
    cooked_js = REQUIREJS_RESET_PREFIX
    siteUrl = getSite().absolute_url()
    request = getRequest()
    for package in bundle.resources or []:
        if package not in resources:
            continue
        resource = resources[package]

        for css_resource in resource.css:
            css_url = siteUrl + '/' + css_resource
            response = subrequest(css_url)
            if response.status == 200:
                css = response.getBody()
                cooked_css += '\n/* Resource: {0} */\n{1}\n'.format(
                    css_resource,
                    css if '.min.css' == css_resource[-8:] else cssmin(css)
                )
            else:
                cooked_css += '\n/* Could not find resource: {0} */\n\n'.format(  # noqa
                    css_resource
                )

        if not resource.js:
            continue
        js_url = siteUrl + '/' + resource.js
        response = subrequest(js_url)
        if response.status == 200:
            js = response.getBody()
            try:
                cooked_js += '\n/* resource: {0} */\n{1}'.format(
                    resource.js,
                    js if '.min.js' == resource.js[-7:] else
                    minify(js, mangle=False, mangle_toplevel=False)
                )
            except SyntaxError:
                cooked_js += '\n/* resource(error cooking): {0} */\n{1}'.format(  # noqa
                    resource.js,
                    js
                )
        else:
            cooked_js += '\n/* Could not find resource: {0} */\n\n'.format(
                js_url
            )

    cooked_js += REQUIREJS_RESET_POSTFIX

    js_path = bundle.jscompilation
    css_path = bundle.csscompilation

    if not js_path:
        logger.warn('Could not compile js/css for bundle as there is '
                    'no jscompilation setting')
        return

    # Storing js
    resource_path = js_path.split('++plone++')[-1]
    resource_name, resource_filepath = resource_path.split('/', 1)
    persistent_directory = getUtility(IResourceDirectory, name="persistent")
    if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
        persistent_directory.makeDirectory(OVERRIDE_RESOURCE_DIRECTORY_NAME)
    container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
    if resource_name not in container:
        container.makeDirectory(resource_name)
    try:
        folder = container[resource_name]
        fi = StringIO(cooked_js)
        folder.writeFile(resource_filepath, fi)

        if css_path:
            # Storing css if defined
            resource_path = css_path.split('++plone++')[-1]
            resource_name, resource_filepath = resource_path.split('/', 1)
            persistent_directory = getUtility(
                IResourceDirectory, name="persistent")
            if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
                persistent_directory.makeDirectory(
                    OVERRIDE_RESOURCE_DIRECTORY_NAME)
            container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
            if resource_name not in container:
                container.makeDirectory(resource_name)
            folder = container[resource_name]
            fi = StringIO(cooked_css)
            folder.writeFile(resource_filepath, fi)
        bundle.last_compilation = datetime.now()
        # setRequest(original_request)
    except NotFound:
        logger.info('Error compiling js/css for the bundle')

    # refresh production meta bundles
    combine_bundles(context)

    # Disable CSRF protection on this request
    alsoProvides(request, IDisableCSRFProtection)
