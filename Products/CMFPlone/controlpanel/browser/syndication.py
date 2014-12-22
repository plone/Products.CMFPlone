from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from zope.i18nmessageid import MessageFactory
from Products.CMFPlone.interfaces.syndication import ISiteSyndicationSettings
from plone.app.registry.browser import controlpanel
from z3c.form import button
from Products.statusmessages.interfaces import IStatusMessage

_ = MessageFactory('plone')


class SyndicationControlPanelForm(controlpanel.RegistryEditForm):
    schema = ISiteSyndicationSettings
    label = _(u'Syndication Settings')
    description = _(u'Default syndication settings.')

    def getSyndicationSettingsButtonShown(self):
        actions = getToolByName(self.context, 'portal_actions')
        if 'syndication' in actions.object.objectIds():
            return actions.object.syndication.getProperty('visible')
        else:
            IStatusMessage(self.request).addStatusMessage(
                _(u"Missing syndication settings action."), "warn")

    def getSyndicationLinkShown(self):
        actions = getToolByName(self.context, 'portal_actions')
        if 'rss' in actions.document_actions.objectIds():
            return actions.document_actions.rss.getProperty('visible')
        else:
            IStatusMessage(self.request).addStatusMessage(
                _(u"Missing rss link action."), "warn")

    def forceCheckboxValue(self, widget, checked):
        if checked:
            widget.value = ['selected']
        else:
            widget.value = []
        for item in widget.items:
            if 'checked' in item:
                if checked:
                    item['checked'] = True
                else:
                    item['checked'] = False

    def update(self):
        super(SyndicationControlPanelForm, self).update()

        # We override this so we can get actual
        # settings for portal_actions related settings
        content = self.getContent()
        show_settings_btn = self.getSyndicationSettingsButtonShown()
        if show_settings_btn != content.show_syndication_button:
            self.forceCheckboxValue(
                self.widgets['show_syndication_button'], show_settings_btn)
        show_link_btn = self.getSyndicationLinkShown()
        if show_link_btn != content.show_syndication_link:
            self.forceCheckboxValue(
                self.widgets['show_syndication_link'], show_link_btn)

    def setSyndicationActionSettings(self, data):
        actions = getToolByName(self.context, 'portal_actions')
        if 'syndication' in actions.object.objectIds():
            actions.object.syndication._setPropValue(
                'visible', data['show_syndication_button'])
        if 'rss' in actions.document_actions.objectIds():
            actions.document_actions.rss._setPropValue(
                'visible', data['show_syndication_link'])

    @button.buttonAndHandler(_(u"Save"), name='save')
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
        IStatusMessage(self.request).addStatusMessage(
            _(u"Changes saved."), "info")
        self.request.response.redirect("%s/%s" % (
            self.context.absolute_url(), self.control_panel_view))

    @button.buttonAndHandler(_(u"Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            _(u"Edit cancelled."), "info")
        self.request.response.redirect("%s/%s" % (
            self.context.absolute_url(), self.control_panel_view))


class SyndicationControlPanel(controlpanel.ControlPanelFormWrapper):
    form = SyndicationControlPanelForm
