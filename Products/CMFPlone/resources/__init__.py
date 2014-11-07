from zope.component import adapter
from plone.app.theming.interfaces import IThemeAppliedEvent


@adapter(IThemeAppliedEvent)
def onThemeApplied(event):
    # check for bundles to enable or disable
    theme = event.theme
    # theme.enabled_bundles
    # theme.disabled_bundles


def add_bundle_on_request(request, bundle):
    """ Adds the bundle to the request
    """
    if hasattr(request, 'enabled_bundles'):
        if isinstance(bundle, str):
            request.enabled_bundles.append(bundle)
    else:
        request.enabled_bundles = [bundle]


def remove_bundle_on_request(request, bundle):
    """ Removes the bundle to the request
    """
    if hasattr(request, 'disabled_bundles'):
        if isinstance(bundle, str):
            request.disabled_bundles.append(bundle)
    else:
        request.disabled_bundles = [bundle]
