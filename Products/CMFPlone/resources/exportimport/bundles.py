from plone.registry.interfaces import IRegistry
from zope.component import queryUtility

from ..browser.combine import combine_bundles


def combine(context):

    logger = context.getLogger('bundles')
    registry = queryUtility(IRegistry)

    if registry is None:
        logger.info("Cannot find registry")
        return

    body = context.readDataFile('registry.xml')
    if body and "IBundleRegistry" in body:
        site = context.getSite()
        combine_bundles(site)
