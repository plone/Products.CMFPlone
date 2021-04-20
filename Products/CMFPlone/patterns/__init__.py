from zope.deferredimport import deprecated

deprecated(
    "Import from Products.CMFPlone.patterns.tinymce instead",
    TinyMCESettingsGenerator="Products.CMFPlone.patterns.tinymce.TinyMCESettingsGenerator",  # noqa: E501
)
deprecated(
    "Import from Products.CMFPlone.patterns.settings instead",
    PloneSettingsAdapter="Products.CMFPlone.patterns.settings.PatternSettingsAdapter",  # noqa: E501
)
