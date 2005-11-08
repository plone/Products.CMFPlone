"""MemberData tool properties setup handlers.

$Id:$
"""

from xml.dom.minidom import parseString

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import INodeExporter
from Products.GenericSetup.interfaces import INodeImporter
from Products.GenericSetup.interfaces import PURGE, UPDATE
from Products.GenericSetup.utils import PrettyDocument

_FILENAME = 'memberdata_properties.xml'

def importMemberDataProperties(context):
    """ Import MemberData tool properties.
    """
    site = context.getSite()
    mode = context.shouldPurge() and PURGE or UPDATE
    ptool = getToolByName(site, 'portal_memberdata')

    body = context.readDataFile(_FILENAME)
    if body is None:
        return 'MemberData tool: Nothing to import.'

    importer = INodeImporter(ptool, None)
    if importer is None:
        return 'MemberData tool: Import adapter misssing.'

    importer.importNode(parseString(body).documentElement, mode=mode)
    return 'MemberData tool imported.'

def exportMemberDataProperties(context):
    """ Export MemberData tool properties .
    """
    site = context.getSite()

    ptool = getToolByName(site, 'portal_memberdata', None)
    if ptool is None:
        return 'MemberData tool: Nothing to export.'

    exporter = INodeExporter(ptool)
    if exporter is None:
        return 'MemberData tool: Export adapter misssing.'

    doc = PrettyDocument()
    doc.appendChild(exporter.exportNode(doc))
    context.writeDataFile(_FILENAME, doc.toprettyxml(' '), 'text/xml')
    return 'MemberData tool exported.'

