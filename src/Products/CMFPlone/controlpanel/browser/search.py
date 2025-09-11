from plone.app.registry.browser import controlpanel
from plone.base import PloneMessageFactory as _
from plone.base.interfaces import ISearchSchema
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory


class SearchControlPanelForm(controlpanel.RegistryEditForm):
    id = "SearchControlPanel"
    label = _("Search Settings")
    schema = ISearchSchema
    schema_prefix = "plone"

    def updateFields(self):
        super().updateFields()
        self.fields["types_not_searched"].widgetFactory = CheckBoxFieldWidget

    def updateWidgets(self):
        super().updateWidgets()
        # Replace vocabulary for 'types_not_searched' with user friendly types
        # to hide "bad" types in control panel.
        vocab = self._friendly_types_vocabulary()
        self.widgets["types_not_searched"].terms.terms = vocab(self.context)
        self.widgets["types_not_searched"].update()

    def applyChanges(self, data):
        # We only get "friendly" types. Add "bad" types from current settings.
        current_types = self.fields["types_not_searched"].field.get(self.getContent())
        all_vocab = queryUtility(
            IVocabularyFactory, "plone.app.vocabularies.PortalTypes"
        )
        all_types = [t.value for t in all_vocab(self.context)]
        friendly_vocab = self._friendly_types_vocabulary()
        friendly_types = [t.value for t in friendly_vocab(self.context)]
        submitted_types = data["types_not_searched"] or []
        new_types = [
            t
            for t in all_types
            if t in submitted_types or (t in current_types and t not in friendly_types)
        ]
        data["types_not_searched"] = tuple(new_types)
        super().applyChanges(data)

    def _friendly_types_vocabulary(self):
        return queryUtility(
            IVocabularyFactory, "plone.app.vocabularies.ReallyUserFriendlyTypes"
        )


class SearchControlPanel(controlpanel.ControlPanelFormWrapper):
    form = SearchControlPanelForm
