#!/usr/bin/env python
# encoding: utf-8
"""
profilesettings.py
"""

#import warnings
#from zope.component import queryAdapter
#from zope.component import queryUtility
from zope.interface import implements

#from Acquisition import aq_inner, aq_base
#from Products.CMFPlone import utils
from Products.Five.browser import BrowserView

from plone.app.users.browser.interfaces import IProfileSettingsPanel

class ProfileSettingsPanel(BrowserView):
    implements(IProfileSettingsPanel)

    
