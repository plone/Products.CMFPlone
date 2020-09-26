from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import transaction_note
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import Interface


class ILoggedOutView(Interface):
    pass


class LogoutView(BrowserView):

    def __call__(self):
        mt = getToolByName(self.context, 'portal_membership')
        mt.logoutUser(self.request)
        transaction_note('Logged out')
        # Handle external logout requests from other portals
        next_ = self.request.get('next', None)
        portal_url = getToolByName(self.context, 'portal_url')
        if next_ is not None and portal_url.isURLInPortal(next_):
            target_url = next_
        else:
            target_url = self.request.URL1 + '/logged-out'

        registry = queryUtility(IRegistry)
        external_logout_url = registry['plone.external_logout_url']
        if external_logout_url:
            target_url = external_logout_url
        self.request.response.redirect(target_url)


@implementer(ILoggedOutView)
class LoggedOutView(BrowserView):

    def __call__(self):
        portal_state = getMultiAdapter(
            (self.context, self.request),
            name='plone_portal_state',
        )
        if portal_state.anonymous():
            IStatusMessage(
                self.request
            ).addStatusMessage(
                _(
                    'statusmessage_logged_out',
                    default='You are now logged out.'
                ),
                'info',
            )
            self.request.response.redirect(
                portal_state.navigation_root_url()
            )
            return
        return self.index()
