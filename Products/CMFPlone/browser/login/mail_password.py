from AccessControl import Unauthorized
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage


class MailPasswordView(BrowserView):

    def __call__(self):
        response = None
        try:
            response = self.context.portal_registration.mailPassword(
                self.request.form.get('userid', ''),
                self.request,
            )
        except ValueError as e:
            try:
                msg = _(str(e))
            except Unauthorized:
                # If we are not allowed to tell the user, what is wrong, he
                # should get an error message and contact the admins
                raise e
            IStatusMessage(self.request).add(msg)
            self.request.response.redirect(
                self.context.absolute_url() + '/mail_password_form'
            )
        return response
