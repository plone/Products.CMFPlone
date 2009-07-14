from zope.interface import Interface
from zope.interface import implements
from Products.Five.browser import BrowserView

from form import AccountPanelForm

class IProfileSettingsPanel(Interface):
    """Base interface for the Profile Settings view"""

class ProfileSettingsPanel(BrowserView, AccountPanelForm):
    implements(IProfileSettingsPanel)

