import os

from Acquisition import aq_base
from Products.CMFPlone.migrations.migration_util import installOrReinstallProduct
from Products.CMFCore import CMFCorePermissions

def two05_alpha1(portal):
    """2.0.5 -> 2.1-alpha1
    """
    out = []

    # Add document actions
    addDocumentActions(portal, out)

    # Add action icons
    addActionIcons(portal, out)
    
    return out
    
def addDocumentActions(portal, out):
    """Adds a full screen mode action. """
    at = portal.portal_actions
    if 'full_screen' not in [action.getId() for action in at.listActions()]:
        at.addAction('full_screen',
             name='Full Screen',
             action='string:javascript:fullscreenMode();',
             condition='member',
             permission=CMFCorePermissions.View,
             category='document_actions',
             visible=1)

def addActionIcons(portal, out):
    """Adds a icon for full screen mode action. """
    ai = portal.portal_actionicons
    if 'full_screen' not in [icon.getId() for icon in ai.listActions()]:
        ai.addActionIcon('plone',
                     'full_screen',
                     'full_screen.gif',
                     'Full Screen')