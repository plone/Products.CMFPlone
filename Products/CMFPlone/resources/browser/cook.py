from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.resources.interfaces import (
    IBundleRegistry,
    IResourceRegistry,
    OVERRIDE_RESOURCE_DIRECTORY_NAME)
from slimit import minify
from cssmin import cssmin
from plone.subrequest import subrequest
from datetime import datetime
from plone.resource.interfaces import IResourceDirectory
from StringIO import StringIO
from zExceptions import NotFound
from zope.component.hooks import getSite



def cookWhenChangingSettings(settings, event):
    """When our settings are changed, re-cook the not compilable bundles
    """

    # search for bundles, cook css/js for each that is not compile
    registry = getUtility(IRegistry)
    bundles = registry.collectionOfInterface(
        IBundleRegistry, prefix="Products.CMFPlone.bundles")
    resources = registry.collectionOfInterface(
        IResourceRegistry, prefix="Products.CMFPlone.resources")

    if event.record.fieldName == 'last_compilation':
        return

    name = str(event.record).split('/')[1]
    siteUrl = getSite().absolute_url()

    for key, bundle in bundles.items():
        is_in_bundle = False
        if bundle.compile is False:
            # Let's join all css and js
            css_file = ""
            js_file = ""
            for package in bundle.resources:
                if package in name:
                    is_in_bundle = True
            if is_in_bundle:
                # If this resource is not in the bundle just skip it
                continue
            for package in bundle.resources:
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
                            js_file += response.getBody()
                            js_file += '\n'
            cooked_js = minify(js_file, mangle=True, mangle_toplevel=True)
            cooked_css = cssmin(css_file)

            js_path = bundle.jscompilation
            css_path = bundle.csscompilation

            # Storing js
            resource_path = js_path.split('++plone++')[-1]
            resource_name, resource_filepath = resource_path.split('/', 1)
            persistent_directory = getUtility(IResourceDirectory, name="persistent")  # noqa
            if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
                persistent_directory.makeDirectory(OVERRIDE_RESOURCE_DIRECTORY_NAME)  # noqa
            container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
            if resource_name not in container:
                container.makeDirectory(resource_name)
            folder = container[resource_name]
            fi = StringIO(cooked_js)
            folder.writeFile(resource_filepath, fi)

            # Storing css
            resource_path = css_path.split('++plone++')[-1]
            resource_name, resource_filepath = resource_path.split('/', 1)
            persistent_directory = getUtility(IResourceDirectory, name="persistent")  # noqa
            if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
                persistent_directory.makeDirectory(OVERRIDE_RESOURCE_DIRECTORY_NAME)  # noqa
            container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
            if resource_name not in container:
                container.makeDirectory(resource_name)
            folder = container[resource_name]
            fi = StringIO(cooked_css)
            folder.writeFile(resource_filepath, fi)
            bundle.last_compilation = datetime.now()