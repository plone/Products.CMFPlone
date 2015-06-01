import os


RESOURCE_DEVELOPMENT_MODE = False
if os.getenv('FEDEV', '').lower() == 'true':
    RESOURCE_DEVELOPMENT_MODE = True


def add_resource_on_request(request, resource):
    """ Adds the resource to the request
    """
    if hasattr(request, 'enabled_resources'):
        if isinstance(resource, str):
            request.enabled_resources.append(resource)
    else:
        request.enabled_resources = [resource]


def add_bundle_on_request(request, bundle):
    """ Adds the bundle to the request
    """
    if hasattr(request, 'enabled_bundles'):
        if isinstance(bundle, str):
            request.enabled_bundles.append(bundle)
    else:
        request.enabled_bundles = [bundle]


def remove_bundle_on_request(request, bundle):
    """ Removes the bundle to the request
    """
    if hasattr(request, 'disabled_bundles'):
        if isinstance(bundle, str):
            request.disabled_bundles.append(bundle)
    else:
        request.disabled_bundles = [bundle]
