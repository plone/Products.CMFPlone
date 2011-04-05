from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFPlone.interfaces import IPloneBaseTool
from Acquisition import aq_base
from Acquisition import aq_parent
from Acquisition import aq_inner

from Products.CMFCore import Expression
from Products.CMFCore.utils import getToolByName

from zope.interface import implements
from zope.component import getMultiAdapter

TempFolderClass = None

# getOAI() and getExprContext copied from CMF 1.5.1+cvs
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
# ZPL 2.1
from Products.CMFCore.ActionInformation import oai


def initializeTFC():
    """To work around circular imports ...
    """
    global TempFolderClass
    if TempFolderClass is None:
        from Products.CMFPlone.FactoryTool import TempFolder
        TempFolderClass = TempFolder


def getOAI(context, object=None):
    initializeTFC()
    request = getattr(context, 'REQUEST', None)
    if request:
        cache = request.get('_oai_cache', None)
        if cache is None:
            request['_oai_cache'] = cache = {}
        info = cache.get(id(object), None)
    else:
        info = None
    if info is None:
        if object is None or not hasattr(object, 'aq_base'):
            folder = None
        else:
            folder = object
            # Search up the containment hierarchy until we find an
            # object that claims it's a folder.
            while folder is not None:
                if getattr(aq_base(folder), 'isPrincipiaFolderish', 0):
                    # found it.
                    break
                else:
                    # If the parent of the object at hand is a TempFolder
                    # don't strip off its outer acquisition context (Plone)
                    parent = aq_parent(aq_inner(folder))
                    if getattr(parent, '__class__', None) == TempFolderClass:
                        folder = aq_parent(folder)
                    else:
                        folder = parent
        info = oai(context, folder, object)
        if request:
            cache[id(object)] = info
    return info


def createExprContext(folder, portal, object):
    expr_context = Expression.createExprContext(folder, portal, object)
    view_obj = object
    if view_obj is None:
        view_obj = portal
    req = view_obj.REQUEST

    expr_context.setGlobal('portal', portal)

    globals_view = getMultiAdapter((view_obj, req), name='plone')
    expr_context.setGlobal('globals_view', globals_view)

    # TODO: For some reason, when using getMultiAdapter() here we get
    # authoriziation problems in some cases (e.g. when using one of these
    # in a python: expression in an action).

    plone_portal_state = view_obj.restrictedTraverse('@@plone_portal_state')
    expr_context.setGlobal('plone_portal_state', plone_portal_state)

    plone_context_state = view_obj.restrictedTraverse('@@plone_context_state')
    expr_context.setGlobal('plone_context_state', plone_context_state)

    plone_tools = view_obj.restrictedTraverse('@@plone_tools')
    expr_context.setGlobal('plone_tools', plone_tools)

    # Add checkPermission to the action expression context to make cleaner
    # faster expressions
    membership_tool = getToolByName(view_obj, 'portal_membership')
    checkPerm = membership_tool.checkPermission
    expr_context.setGlobal('checkPermission', checkPerm)

    # add 'context' as an alias for 'object'
    expr_context.setGlobal('context', object)

    # need this for resolving in Unicode expressions
    expr_context.setContext('context', object)

    return expr_context


def getExprContext(context, object=None):
    initializeTFC()
    request = getattr(context, 'REQUEST', None)
    if request:
        cache = request.get('_plone_ec_cache', None)
        if cache is None:
            request['_plone_ec_cache'] = cache = {}
        ec = cache.get(id(object), None)
    else:
        ec = None
    if ec is None:
        utool = getToolByName(context, 'portal_url')
        portal = utool.getPortalObject()
        if object is None or not hasattr(object, 'aq_base'):
            folder = portal
        else:
            folder = object
            # Search up the containment hierarchy until we find an
            # object that claims it's a folder.
            while folder is not None:
                if getattr(aq_base(folder), 'isPrincipiaFolderish', 0):
                    # found it.
                    break
                else:
                    # If the parent of the object at hand is a TempFolder
                    # don't strip off its outer acquisition context (Plone)
                    parent = aq_parent(aq_inner(folder))
                    if getattr(parent, '__class__', None) == TempFolderClass:
                        folder = aq_parent(folder)
                    else:
                        folder = parent
        ec = createExprContext(folder, portal, object)
        if request:
            cache[id(object)] = ec
    return ec


class PloneBaseTool:
    """Base class of all tools used in CMFPlone and Plone Core
    """

    security = ClassSecurityInfo()

    implements(IPloneBaseTool)

    # overwrite getOAI and getExprContext to use our variants that understand the
    # temp folder of portal factory
    def _getOAI(self, object):
        return getOAI(self, object)

    def _getExprContext(self, object):
        return getExprContext(self, object)


InitializeClass(PloneBaseTool)
