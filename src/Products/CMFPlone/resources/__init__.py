from zope.deprecation import deprecate

import os


RESOURCE_DEVELOPMENT_MODE = os.getenv("FEDEV", "").lower() == "true"


@deprecate(
    "Adding single resources is no longer supported in Plone 6, use 'add_bundle_on_request' instead"
)
def add_resource_on_request(request, resource):
    """(DEPRECATED) Adds the resource to the request."""
    return


def add_bundle_on_request(request, bundle):
    """Adds the bundle to the request."""
    if not isinstance(bundle, str):
        raise ValueError("add_bundle_on_request expects a string value for bundle")
    request.enabled_bundles = getattr(request, "enabled_bundles", [])
    if bundle not in request.enabled_bundles:
        request.enabled_bundles.append(bundle)


def remove_bundle_on_request(request, bundle):
    """Removes the bundle to the request."""
    if not isinstance(bundle, str):
        raise ValueError("remove_bundle_on_request expects a string value for bundle")
    request.disabled_bundles = getattr(request, "disabled_bundles", [])
    if bundle not in request.disabled_bundles:
        request.disabled_bundles.append(bundle)
