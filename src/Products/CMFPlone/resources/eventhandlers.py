from Products.CMFPlone.resources.browser.resource import update_resource_registry_mtime
from Products.GenericSetup.interfaces import IProfileImportedEvent
from zope.component import adapter


@adapter(IProfileImportedEvent)
def check_registry_update(event):
    """Check if a profile import may have updated the configuration registry.

    Main concern for now is: the resource registries may have changed.
    This means the resource viewlet caches should be cleared.
    See discussion in https://github.com/plone/Products.CMFPlone/issues/3505
    """
    if not (event.full_import or "plone.app.registry" in event.steps):
        return
    update_resource_registry_mtime()
