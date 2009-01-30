#!/usr/bin/env python
# encoding: utf-8
"""
interfaces.py

Created by David Convent on 2009-01-30.
Copyright (c) 2009 davconvent. All rights reserved.
"""

from zope.interface import Interface
from plone.app.controlpanel.interfaces import IPloneControlPanelView

class IAccountPanelView(IPloneControlPanelView):
    """A marker interface for views showing an account panel.
    """


class IAccountPanelForm(IPloneControlPanelView):
    """Forms using plone.app.users
    """
    
    def _on_save():
        """Callback mehod which can be implemented by control panels to
        react when the form is successfully saved. This avoids the need
        to re-define actions only to do some additional notification or
        configuration which cannot be handled by the normal schema adapter.
        
        By default, does nothing.
        """


class IPersonalPreferencesPanel(Interface):
    """An interface for the account settings page.
    """
    
class IUserDataPanel(Interface):
    """An interface for the account settings page.
    """
    
class IProfileSettingsPanel(Interface):
    """An interface for the account settings page.
    """
    
