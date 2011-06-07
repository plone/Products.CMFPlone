##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Plone control panel tool node adapters.

$Id$
"""
from zope.i18nmessageid import Message

from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import XMLAdapterBase

from Products.CMFCore.interfaces import IActionProvider
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.interfaces import IControlPanel


class ControlPanelXMLAdapter(XMLAdapterBase):

    """
    XML im- and exporter for Plone control panel.  Most of this
    code is taken from the actions handler in CMFCore.
    """

    __used_for__ = IControlPanel

    _LOGGER_ID = 'controlpanel'

    name = 'controlpanel'

    def _exportNode(self):
        """
        Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractConfiglets())
        self._logger.info('Control panel exported.')
        return node

    def _importNode(self, node):
        """
        Import the object from the DOM node.
        """
        self._initProvider(node)
        self._logger.info('Control panel imported.')

    def _initProvider(self, node):
        if self.environ.shouldPurge():
            actions = self.context.listActions()
            for action in actions:
                self.context.unregisterConfiglet(action.getId())

        self._initConfiglets(node)

    def _extractConfiglets(self):
        fragment = self._doc.createDocumentFragment()

        provider = self.context
        if not IActionProvider.providedBy(provider):
            return fragment

        actions = provider.listActions()

        if actions and isinstance(actions[0], dict):
            return fragment

        for ai in actions:
            mapping = ai.getMapping()
            child = self._doc.createElement('configlet')
            child.setAttribute('action_id', mapping['id'])
            child.setAttribute('category', mapping['category'])
            child.setAttribute('condition_expr', mapping['condition'])
            child.setAttribute('title', mapping['title'])
            child.setAttribute('url_expr', mapping['action'])
            child.setAttribute('visible', str(mapping['visible']))
            child.setAttribute('appId', ai.getAppId())
            child.setAttribute('icon_expr', mapping['icon_expr'])
            for permission in mapping['permissions']:
                sub = self._doc.createElement('permission')
                sub.appendChild(self._doc.createTextNode(permission))
                child.appendChild(sub)
            fragment.appendChild(child)
        return fragment

    def _initConfiglets(self, node):
        controlpanel = self.context
        default_domain = "plone"
        if node.nodeName == 'object':
            domain = str(node.getAttribute('i18n:domain'))
            if domain:
                default_domain = domain
        for child in node.childNodes:
            if child.nodeName != 'configlet':
                continue

            domain = str(child.getAttribute('i18n:domain'))
            if not domain:
                domain = default_domain

            action_id = str(child.getAttribute('action_id'))
            title = Message(str(child.getAttribute('title')), domain=domain)
            url_expr = str(child.getAttribute('url_expr'))
            condition_expr = str(child.getAttribute('condition_expr'))
            icon_expr = str(child.getAttribute('icon_expr'))
            category = str(child.getAttribute('category'))
            visible = str(child.getAttribute('visible'))
            appId = str(child.getAttribute('appId'))
            if visible.lower() == 'true':
                visible = 1
            else:
                visible = 0

            permission = ''
            for permNode in child.childNodes:
                if permNode.nodeName == 'permission':
                    for textNode in permNode.childNodes:
                        if textNode.nodeName != '#text' or \
                               not textNode.nodeValue.strip():
                            continue
                        permission = str(textNode.nodeValue)
                        break  # only one permission is allowed
                    if permission:
                        break

            # Remove previous action with same id and category.
            controlpanel.unregisterConfiglet(action_id)

            controlpanel.registerConfiglet(id=action_id,
                                           name=title,
                                           action=url_expr,
                                           appId=appId,
                                           condition=condition_expr,
                                           category=category,
                                           permission=permission,
                                           visible=visible,
                                           icon_expr=icon_expr)


def importControlPanel(context):
    """Import Plone control panel.
    """
    site = context.getSite()
    tool = getToolByName(site, 'portal_controlpanel', None)
    if tool is None:
        return

    importObjects(tool, '', context)


def exportControlPanel(context):
    """Export actions tool.
    """
    site = context.getSite()
    tool = getToolByName(site, 'portal_controlpanel', None)
    if tool is None:
        return

    exportObjects(tool, '', context)
