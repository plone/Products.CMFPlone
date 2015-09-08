import logging

from Products.CMFPlone.interfaces.resources import IResourceRegistry
from Products.CMFPlone.interfaces.resources import IBundleRegistry
from Products.CMFPlone.interfaces.resources import OVERRIDE_RESOURCE_DIRECTORY_NAME  # noqa
from StringIO import StringIO
from cssmin import cssmin
from datetime import datetime
from plone.protect.interfaces import IDisableCSRFProtection
from plone.registry.interfaces import IRegistry
from plone.resource.interfaces import IResourceDirectory
from plone.subrequest import subrequest
from slimit import minify
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zExceptions import NotFound

logger = logging.getLogger('Products.CMFPlone')


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

    # Let's join all css and js
    css_file = ""
    cooked_js = """
/* reset requirejs definitions so that people who
   put requirejs in legacy compilation do not get errors */
var _old_define = define;
var _old_require = require;
define = undefined;
require = undefined;
try{
"""
    siteUrl = getSite().absolute_url()
    request = getRequest()
    for package in bundle.resources or []:
        if package in resources:
            resource = resources[package]
            for css in resource.css:
                response = subrequest(siteUrl + '/' + css)
                if response.status == 200:
                    css_file += response.getBody()
                    css_file += '\n'

            if resource.js:
                response = subrequest(siteUrl + '/' + resource.js)
                if response.status == 200:
                    js = response.getBody()
                    try:
                        cooked_js += '\n/* resource: %s */\n%s' % (
                            resource.js,
                            minify(js, mangle=False, mangle_toplevel=False)
                        )
                    except SyntaxError:
                        cooked_js += '\n/* resource(error cooking): %s */\n%s' % (
                            resource.js, js)
                else:
                    cooked_js += '\n/* Could not find resource: %s */\n\n' % resource.js

    cooked_js += """
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
    cooked_css = cssmin(css_file)

    js_path = bundle.jscompilation
    css_path = bundle.csscompilation

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
            persistent_directory = getUtility(IResourceDirectory, name="persistent")
            if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
                persistent_directory.makeDirectory(OVERRIDE_RESOURCE_DIRECTORY_NAME)
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
    # Disable CSRF protection on this request
    alsoProvides(request, IDisableCSRFProtection)
