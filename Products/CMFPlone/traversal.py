from plone.base.interfaces.resources import OVERRIDE_RESOURCE_DIRECTORY_NAME
from plone.resource.interfaces import IResourceDirectory
from plone.resource.traversal import ResourceTraverser
from Products.PageTemplates.Expressions import getEngine
from Products.PageTemplates.Expressions import getTrustedEngine
from Products.PageTemplates.interfaces import IZopeAwareEngine
from zope.component import queryUtility
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.pagetemplate import engine as zpt_engine


class PloneBundlesTraverser(ResourceTraverser):
    # the name is misleading - it is used not only for bundles.
    # in fact in Plone 6 bundles are no longer used, despite that the traverser
    # might be in use for other use cases.

    name = "plone"

    def traverse(self, name, remaining):
        # in case its not a request get the default one
        req = getRequest()
        if not req or "PATH_INFO" not in req.environ:
            return super().traverse(name, remaining)

        resource_path = req.environ["PATH_INFO"].split("++plone++")[-1]
        try:
            resource_name, resource_filepath = resource_path.split("/", 1)
        except ValueError:
            # Not the path info / url that we expected.
            # So the request is not for a resource,
            # but for a page that traverses to a resource.
            # The standard resource traverser can handle this.
            return super().traverse(name, remaining)

        # If we have additional traversers in the path we should not use them
        # in the file lookup
        if resource_filepath.startswith("++") or resource_filepath.startswith("@@"):
            resource_filepath = resource_filepath.split("/")[-1]

        persistentDirectory = queryUtility(IResourceDirectory, name="persistent")
        directory = None
        if (
            persistentDirectory is not None
            and OVERRIDE_RESOURCE_DIRECTORY_NAME in persistentDirectory
        ):
            container = persistentDirectory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
            if resource_name in container:
                directory = container[resource_name]
                if resource_filepath in directory:
                    return directory
        return super().traverse(name, remaining)


@implementer(IZopeAwareEngine)
def get_zope_page_template_engine(engine):
    """Get Zope-aware page template engine.

    Hopefully a trusted one, but maybe an untrusted one,
    with less possibilities and more security checks.
    We fall back to nothing. This means the original engine will be used.

    Needed since the page template refactoring/cleanup in Zope 4.4.
    See https://github.com/plone/Products.CMFPlone/issues/3141

    This is currently expected to only be called when a zope.pagetemplate
    is being rendered, which can happen with z3c.form related code.
    For Products.PageTemplates, this code should not be needed.
    """
    if isinstance(engine, zpt_engine.ZopeEngine):
        # Get untrusted engine.
        return getEngine()
    if isinstance(engine, zpt_engine.TrustedZopeEngine):
        return getTrustedEngine()
