# -*- coding: utf-8 -*-
from ..browser.combine import combine_bundles
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility
from zope.globalrequest import getRequest


def combine(context):
    logger = context.getLogger('bundles')
    registry = queryUtility(IRegistry)

    if registry is None:
        logger.info("Cannot find registry")
        return

    # Look for a keyword in registry.xml or the registry directory.
    filepaths = ['registry.xml']
    if context.isDirectory('registry'):
        for filename in context.listDirectory('registry'):
            filepaths.append('registry/' + filename)
    found = False
    for filepath in filepaths:
        body = context.readDataFile(filepath)
        if body is not None and b'IBundleRegistry' in body:
            found = True
            break
    if not found:
        return

    # Calling combine_bundles will have as side effect that the
    # Content-Type header of the response is set to application/javascript,
    # which we do not want.  So we reset it to the original at the end.
    site = context.getSite()
    request = getattr(site, 'REQUEST', getRequest())
    # In tests the request can easily be None.
    if request is not None:
        orig_header = request.response.getHeader('Content-Type')
    combine_bundles(site)
    if request is None:
        # we are done
        return
    new_header = request.response.getHeader('Content-Type')
    if new_header == orig_header:
        return
    if orig_header is None:
        # Setting it to None would result in the string 'None'.
        # So pick a saner one.
        orig_header = 'text/html'
    request.response.setHeader('Content-Type', orig_header)
