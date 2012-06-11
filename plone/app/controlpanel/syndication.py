from zope.i18nmessageid import MessageFactory
from Products.CMFPlone.interfaces.syndication import ISiteSyndicationSettings
from plone.app.registry.browser import controlpanel

_ = MessageFactory('plone')


class SyndicationControlPanelForm(controlpanel.RegistryEditForm):
    schema = ISiteSyndicationSettings
    label = _(u'Syndication Settings')
    description = _(u'Default syndication settings.')


class SyndicationControlPanel(controlpanel.ControlPanelFormWrapper):
    form = SyndicationControlPanelForm
