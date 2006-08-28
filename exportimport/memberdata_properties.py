"""MemberData tool properties setup handlers.

$Id:$
"""

from zope.app import zapi
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import IBody

_FILENAME = 'memberdata_properties.xml'

def importMemberDataProperties(context):
    """ Import MemberData tool properties.
    """
    site = context.getSite()
    logger = context.getLogger('memberdata')
    ptool = getToolByName(site, 'portal_memberdata')

    body = context.readDataFile(_FILENAME)
    if body is None:
        logger.info('Nothing to import.')
        return

    importer = zapi.queryMultiAdapter((ptool, context), IBody)
    if importer is None:
        logger.warning('Import adapter missing.')
        return

    importer.body = body
    logger.info('MemberData tool imported.')

def exportMemberDataProperties(context):
    """ Export MemberData tool properties .
    """
    site = context.getSite()
    logger = context.getLogger('memberdata')
    ptool = getToolByName(site, 'portal_memberdata', None)
    if ptool is None:
        logger.info('Nothing to export.')
        return

    exporter = zapi.queryMultiAdapter((ptool, context), IBody)
    if exporter is None:
        logger.warning('Export adapter missing.')
        return

    context.writeDataFile(_FILENAME, exporter.body, exporter.mime_type)
    logger.info('MemberData tool exported.')

