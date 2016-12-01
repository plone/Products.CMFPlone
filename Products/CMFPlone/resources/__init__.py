# -*- coding: utf-8 -*-
import os


RESOURCE_DEVELOPMENT_MODE = os.getenv('FEDEV', '').lower() == 'true'


def add_resource_on_request(request, resource):
    """ Adds the resource to the request
    """
    if not isinstance(resource, str):
        raise ValueError(
            'add_resource_on_request expects a string value for resource'
        )
    request.enabled_resources = getattr(request, 'enabled_resources', [])
    if resource not in request.enabled_resources:
        request.enabled_resources.append(resource)


def add_bundle_on_request(request, bundle):
    """ Adds the bundle to the request
    """
    if not isinstance(bundle, str):
        raise ValueError(
            'add_bundle_on_request expects a string value for bundle'
        )
    request.enabled_bundles = getattr(request, 'enabled_bundles', [])
    if bundle not in request.enabled_bundles:
        request.enabled_bundles.append(bundle)


def remove_bundle_on_request(request, bundle):
    """ Removes the bundle to the request
    """
    if not isinstance(bundle, str):
        raise ValueError(
            'remove_bundle_on_request expects a string value for bundle'
        )
    request.disabled_bundles = getattr(request, 'disabled_bundles', [])
    if bundle not in request.disabled_bundles:
        request.disabled_bundles.append(bundle)
