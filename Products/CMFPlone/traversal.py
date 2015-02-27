from plone.resource.traversal import ResourceTraverser
from zope.component import getUtility
from plone.resource.interfaces import IResourceDirectory
from Products.CMFPlone.interfaces.resources import (
    OVERRIDE_RESOURCE_DIRECTORY_NAME)
from zope.globalrequest import getRequest


class PloneBundlesTraverser(ResourceTraverser):

    name = 'plone'

    def traverse(self, name, remaining):
        # in case its not a request get the default one
        req = getRequest()
        if 'PATH_INFO' not in req.environ:
            return super(PloneBundlesTraverser, self).traverse(name, remaining)

        resource_path = req.environ['PATH_INFO'].split('++plone++')[-1]
        resource_name, resource_filepath = resource_path.split('/', 1)

        persistentDirectory = getUtility(IResourceDirectory, name="persistent")
        directory = None
        if OVERRIDE_RESOURCE_DIRECTORY_NAME in persistentDirectory:
            container = persistentDirectory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
            if resource_name in container:
                directory = container[resource_name]
                try:
                    return directory[resource_filepath]
                except:
                    pass
        return super(PloneBundlesTraverser, self).traverse(name, remaining)