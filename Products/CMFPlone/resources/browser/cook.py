from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.resources import (
    IBundleRegistry,
    IResourceRegistry,
    OVERRIDE_RESOURCE_DIRECTORY_NAME)
from slimit import minify
from cssmin import cssmin
from datetime import datetime
from plone.resource.interfaces import IResourceDirectory
from StringIO import StringIO
from zope.component.hooks import getSite
from Products.Five.browser.resource import Resource as z3_Resource

from Products.CMFCore.FSFile import FSFile


def cookWhenChangingSettings(context, bundle):
    """When our settings are changed, re-cook the not compilable bundles
    """
    registry = getUtility(IRegistry)
    resources = registry.collectionOfInterface(
        IResourceRegistry, prefix="plone.resources")

    # Let's join all css and js
    css_file = ""
    js_file = ""
    for package in bundle.resources:
        if package in resources:
            resource = resources[package]
            for css in resource.css:
                css_obj = getSite().restrictedTraverse(css, None)
                if css_obj:
                    try:
                        path = css_obj.chooseContext().path
                        css_file += open(path, 'r').read()
                        css_file += '\n'
                    except:
                        if isinstance(css_obj, FSFile):
                            js_file += str(css_obj)
                        elif callable(css_obj):
                            css_file += css_obj().encode('utf-8')

            if resource.js:
                js_obj = getSite().restrictedTraverse(resource.js, None)
                if js_obj:
                    try:
                        path = js_obj.chooseContext().path
                        js_file += open(path, 'r').read()
                        js_file += '\n'
                    except:
                        if isinstance(js_obj, FSFile):
                            js_file += str(js_obj)
                        elif callable(js_obj):
                            js_file += js_obj().encode('utf-8')

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
    import transaction
    transaction.commit()