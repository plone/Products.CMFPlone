#!/usr/bin/env python
# encoding: utf-8
"""
profilesettings.py
"""

from zope.interface import Interface
from zope.interface import implements
from Products.Five.browser import BrowserView

class IProfileSettingsPanel(Interface):
    """Base interface for the Profile Settings view"""

class ProfileSettingsPanel(BrowserView):
    implements(IProfileSettingsPanel)

