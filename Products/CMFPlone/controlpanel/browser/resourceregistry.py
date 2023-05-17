from App.config import getConfiguration
from plone.base import PloneMessageFactory as _
from plone.base.interfaces import IBundleRegistry
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.resources.browser.resource import update_resource_registry_mtime
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getUtility

import operator


class ResourceRegistryControlPanelView(BrowserView):
    @property
    def _bundles(self):
        registry = getUtility(IRegistry)
        return registry.collectionOfInterface(
            IBundleRegistry, prefix="plone.bundles", check=False
        )

    @property
    def bundles_data(self):
        result = []
        for name, record in self._bundles.items():
            result.append(
                {
                    "name": name,
                    "safe_name": name.replace(".", "-"),
                    "jscompilation": record.jscompilation,
                    "csscompilation": record.csscompilation,
                    "expression": record.expression,
                    "enabled": record.enabled,
                    "depends": record.depends,
                    "load_async": record.load_async,
                    "load_defer": record.load_defer,
                }
            )
        result = list(sorted(result, key=operator.itemgetter("name")))
        result.append(
            {
                "name": "",
                "safe_name": "",
                "jscompilation": "",
                "csscompilation": "",
                "expression": "",
                "enabled": False,
                "depends": "",
                "load_async": False,
                "load_defer": False,
            }
        )
        return result

    def global_debug_mode(self):
        return getConfiguration().debug_mode

    def debug_mode(self):
        registry = getUtility(IRegistry)
        return registry["plone.resources.development"]

    def _add(self):
        name = self.request.form.get("name", None)
        if name is None or name == "":
            IStatusMessage(self.request).addStatusMessage(
                _("Name can not be empty."), "error"
            )
            return
        bundles = self._bundles
        if name in bundles:
            IStatusMessage(self.request).addStatusMessage(
                _("Record ${name} already exists.", mapping=dict(name=name)), "error"
            )
            return
        record = bundles.add(name)
        self._set_data_from_form(record)
        IStatusMessage(self.request).addStatusMessage(
            _("Record ${name} created.", mapping=dict(name=name)), "info"
        )

    def _update(self):
        new_name = self.request.form.get("name", None)
        if new_name is None or new_name == "":
            IStatusMessage(self.request).addStatusMessage(
                _("Name can not be empty."), "error"
            )
            return
        original_name = self.request.form.get("original_name", None)
        bundles = self._bundles
        if new_name != original_name:
            if original_name not in bundles:
                IStatusMessage(self.request).addStatusMessage(
                    _("Expected record missing."), "error"
                )
                return
            if new_name in bundles:
                IStatusMessage(self.request).addStatusMessage(
                    _(
                        "Record name ${new_name} already taken.",
                        mapping=dict(new_name=new_name),
                    ),
                    "error",
                )
                return
            record = bundles[original_name]
            del bundles[original_name]
            # update prefix
            record.__prefix__ = record.__prefix__.replace(original_name, new_name)
            bundles[new_name] = record
        else:
            record = bundles[original_name]
        self._set_data_from_form(record)
        IStatusMessage(self.request).addStatusMessage(_("Changes saved."), "info")

    def _set_data_from_form(self, record):
        names = record.__schema__.names()
        data = {k: v for k, v in self.request.form.items() if k in names}
        bool_names = ["enabled", "load_async", "load_defer"]
        for bool_name in bool_names:
            data[bool_name] = bool_name in data
        for field_name, value in data.items():
            full_name = record.__prefix__ + field_name
            record.__registry__[full_name] = value
        self._switch_cache(False)

    def _delete(self):
        name = self.request.form.get("original_name", None)
        bundles = self._bundles
        if name not in bundles:
            IStatusMessage(self.request).addStatusMessage(
                _("Expected record ${name} missing.", mapping=dict(name=name)), "error"
            )
            return
        del bundles[name]
        self._switch_cache(False)
        IStatusMessage(self.request).addStatusMessage(_("Record deleted."), "info")

    def _switch_cache(self, state):
        registry = getUtility(IRegistry)
        registry["plone.resources.development"] = state

    def process_form(self):
        if self.request["method"] != "POST":
            return
        action = self.request.form["action"]
        if action == "add":
            self._add()
        elif action == "update":
            self._update()
        elif action == "delete":
            self._delete()
        elif action == "activate_cache":
            self._switch_cache(True)
        elif action == "deactivate_cache":
            self._switch_cache(False)
        else:
            raise ValueError("Invalid form data")
        update_resource_registry_mtime()
        self.request.response.redirect(self.request["ACTUAL_URL"])
