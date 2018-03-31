# -*- coding: utf-8 -*-
from ..browser.combine import combine_bundles
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility
from zope.globalrequest import getRequest

import six


def combine(context):
    if six.PY3:
        return

    logger = context.getLogger('bundles')
    registry = queryUtility(IRegistry)

    if registry is None:
        logger.info("Cannot find registry")
        return

    body = context.readDataFile('registry.xml')
    if body and "IBundleRegistry" in body:
        # Calling combine_bundles will have as side effect that the
        # Content-Type header of the response is set to application/javascript,
        # which we do not want.  So we reset it to the original at the end.
        site = context.getSite()
        request = getattr(site, 'REQUEST', getRequest())
        if request is not None:
            # Easily happens in tests.
            orig_header = request.response.getHeader('Content-Type')
        combine_bundles(site)
        if request is not None:
            new_header = request.response.getHeader('Content-Type')
            if new_header != orig_header:
                if orig_header is None:
                    # Setting it to None would result in the string 'None'.
                    # So pick a saner one.
                    orig_header = 'text/html'
                request.response.setHeader('Content-Type', orig_header)
