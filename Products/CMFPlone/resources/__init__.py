import os


RESOURCE_DEVELOPMENT_MODE = False
if os.getenv('FEDEV', '').lower() == 'true':
    RESOURCE_DEVELOPMENT_MODE = True


def add_resource_on_request(request, resource):
    """ Adds the resource to the request
    """
    if not hasattr(request, 'enabled_resources'):
        request.enabled_resources = []

    if isinstance(resource, str) and resource not in request.enabled_resources:
        request.enabled_resources.append(resource)


def add_bundle_on_request(request, bundle):
    """ Adds the bundle to the request
    """
    if not hasattr(request, 'enabled_bundles'):
        request.enabled_bundles = []

    if isinstance(bundle, str) and bundle not in request.enabled_bundles:
        request.enabled_bundles.append(bundle)


def remove_bundle_on_request(request, bundle):
    """ Removes the bundle to the request
    """
    if hasattr(request, 'disabled_bundles'):
        if isinstance(bundle, str):
            request.disabled_bundles.append(bundle)
    else:
        request.disabled_bundles = [bundle]
