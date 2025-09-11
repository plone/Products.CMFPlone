from plone.base.interfaces import IEditingSchema
from plone.base.interfaces import IPloneSiteRoot
from plone.registry.interfaces import IRegistry
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer


@adapter(IPloneSiteRoot)
@implementer(IEditingSchema)
class EditingControlPanelAdapter:
    def __init__(self, context):
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IEditingSchema, prefix="plone")

    def get_visible_ids(self):
        return self.settings.visible_ids

    def set_visible_ids(self, value):
        self.settings.visible_ids = value

    def get_enable_link_integrity_checks(self):
        return self.settings.enable_link_integrity_checks

    def set_enable_link_integrity_checks(self, value):
        self.settings.enable_link_integrity_checks = value

    def get_ext_editor(self):
        return self.settings.ext_editor

    def set_ext_editor(self, value):
        self.settings.ext_editor = value

    def get_default_editor(self):
        return self.settings.default_editor

    def set_default_editor(self, value):
        self.settings.default_editor = value

    def get_lock_on_ttw_edit(self):
        return self.settings.lock_on_ttw_edit

    def set_lock_on_ttw_edit(self, value):
        self.settings.lock_on_ttw_edit = value

    visible_ids = property(get_visible_ids, set_visible_ids)
    enable_link_integrity_checks = property(
        get_enable_link_integrity_checks, set_enable_link_integrity_checks
    )
    ext_editor = property(get_ext_editor, set_ext_editor)
    default_editor = property(get_default_editor, set_default_editor)
    lock_on_ttw_edit = property(get_lock_on_ttw_edit, set_lock_on_ttw_edit)
