# -*- coding: utf-8 -*-
from ..browser.combine import combine_bundles
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility


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

    # Calling combine_bundles used to have as side effect that the
    # Content-Type header of the response was set to application/javascript,
    # which we do not want.  But that was fixed already in Plone 5.1b2.
    # See https://github.com/plone/Products.CMFPlone/pull/1924
    site = context.getSite()
    combine_bundles(site)
