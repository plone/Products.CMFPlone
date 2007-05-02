from zope.interface import Interface

class IPloneControlPanelForm(Interface):
    """Forms using plone.app.controlpanel
    """
    
    def _on_save():
        """Callback mehod which can be implemented by control panels to
        react when the form is successfully saved. This avoids the need
        to re-define actions only to do some additional notification or
        configuration which cannot be handled by the normal schema adapter.
        
        By default, does nothing.
        """