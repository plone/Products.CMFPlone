from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter


class UserActionsView(BrowserView):
    """Power the useraction fallback page
    """

    def user_actions(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')

        actions = context_state.actions('user')
        return actions
