from plone.app.controlpanel.interfaces import IPloneControlPanelView, IPloneControlPanelForm

class IAccountPanelView(IPloneControlPanelView):
    """A marker interface for views showing an account panel.
    """


class IAccountPanelForm(IPloneControlPanelForm):
    """Forms using plone.app.users
    """
    
    def _on_save():
        """Callback mehod which can be implemented by control panels to
        react when the form is successfully saved. This avoids the need
        to re-define actions only to do some additional notification or
        configuration which cannot be handled by the normal schema adapter.
        
        By default, does nothing.
        """
