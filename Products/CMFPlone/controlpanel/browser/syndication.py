from plone.app.registry.browser import controlpanel
from plone.app.z3cform.widget import SelectFieldWidget
from plone.base.interfaces.syndication import ISiteSyndicationSettings
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("plone")


class SyndicationControlPanelForm(controlpanel.RegistryEditForm):
    schema = ISiteSyndicationSettings
    label = _("Syndication Settings")
    description = _("Default syndication settings.")

    def updateFields(self):
        super().updateFields()
        self.fields["site_rss_items"].widgetFactory = SelectFieldWidget

    def getSyndicationSettingsButtonShown(self):
        actions = getToolByName(self.context, "portal_actions")
        if "syndication" in actions.object.objectIds():
            return actions.object.syndication.getProperty("visible")
        else:
            IStatusMessage(self.request).addStatusMessage(
                _("Missing syndication settings action."), "warn"
            )

    def getSyndicationLinkShown(self):
        actions = getToolByName(self.context, "portal_actions")
        if "rss" in actions.document_actions.objectIds():
            return actions.document_actions.rss.getProperty("visible")
        else:
            IStatusMessage(self.request).addStatusMessage(
                _("Missing rss link action."), "warn"
            )

    def forceCheckboxValue(self, widget, checked):
        if checked:
            widget.value = ["selected"]
        else:
            widget.value = []
        for item in widget.items:
            if "checked" in item:
                if checked:
                    item["checked"] = True
                else:
                    item["checked"] = False

    def update(self):
        super().update()

        # We override this so we can get actual
        # settings for portal_actions related settings
        content = self.getContent()
        show_settings_btn = self.getSyndicationSettingsButtonShown()
        if show_settings_btn != content.show_syndication_button:
            self.forceCheckboxValue(
                self.widgets["show_syndication_button"], show_settings_btn
            )
        show_link_btn = self.getSyndicationLinkShown()
        if show_link_btn != content.show_syndication_link:
            self.forceCheckboxValue(
                self.widgets["show_syndication_link"], show_link_btn
            )

    def setSyndicationActionSettings(self, data):
        actions = getToolByName(self.context, "portal_actions")
        if "syndication" in actions.object.objectIds():
            actions.object.syndication._setPropValue(
                "visible", data["show_syndication_button"]
            )
        if "rss" in actions.document_actions.objectIds():
            actions.document_actions.rss._setPropValue(
                "visible", data["show_syndication_link"]
            )

    @button.buttonAndHandler(_("Save"), name="save")
    def handleSave(self, action):
        """
        Again, we're customizing this to handle saving
        portal_actions related setting data.
        """
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.setSyndicationActionSettings(data)
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_("Changes saved."), "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_("Cancel"), name="cancel")
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Edit cancelled."), "info")
        self.request.response.redirect(self.request.getURL())


class SyndicationControlPanel(controlpanel.ControlPanelFormWrapper):
    form = SyndicationControlPanelForm
