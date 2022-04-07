from zope.deferredimport import deprecated

deprecated(
    "Moved to plone.base.defaultpage, import from there instead (will be removed in Plone 7).",
    DefaultPage="plone.base.defaultpage:DefaultPageView",
)