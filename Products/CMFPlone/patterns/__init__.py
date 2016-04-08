# -*- coding: utf-8 -*-
from zope.deferredimport import deprecated

deprecated(
    "Import from Products.CMFPlone.patterns.tinymce instead",
    TinyMCESettingsGenerator='Products.CMFPlone.patterns.tinymce.'
                             'TinyMCESettingsGenerator'
)
deprecated(
    "Import from Products.CMFPlone.patterns.settings instead",
    PloneSettingsAdapter='Products.CMFPlone.patterns.settings.'
                         'PatternSettingsAdapter'
)
