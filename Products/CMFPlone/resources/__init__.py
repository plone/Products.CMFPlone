from zope.component import adapter
from plone.app.theming.interfaces import IThemeAppliedEvent


@adapter(IThemeAppliedEvent)
def onThemeApplied(event):
    # check for bundles to enable or disable
    theme = event.theme
    # theme.enabled_bundles
    # theme.disabled_bundles
