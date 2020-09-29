from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import IMailSchema
from transaction._transaction import Status
from zope.component import getUtility
from zope.sendmail.mailer import _SMTPState
from zope.sendmail.mailer import SMTPMailer

import logging
import transaction


log = logging.getLogger("MailDataManager")


# BBB remove when zope.sendmail 3.8.0 is released.
def catchAllExceptions(func):
    def _catch(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            txn = transaction.get()
            if txn.status == Status.ACTIVE:
                # sent with immediate=True
                raise
            else:
                # Avoid raising errors during tpc_finish as these could lead to
                # inconsistent state
                log.exception(e)

    return _catch


def applyPatches():
    from zope.sendmail.mailer import SMTPMailer
    old_mailer = getattr(SMTPMailer, 'vote', None) is None
    if old_mailer:
        SMTPMailer.send = catchAllExceptions(SMTPMailer.send)


def new_init(
        self,
        hostname='localhost',
        port=25,
        username=None,
        password=None,
        no_tls=False,
        force_tls=False):

    registry = getUtility(IRegistry)
    mail_settings = registry.forInterface(IMailSchema, prefix='plone')
    self.hostname = mail_settings.smtp_host
    self.port = mail_settings.smtp_port
    self.username = mail_settings.smtp_userid
    self.password = mail_settings.smtp_pass
    self.force_tls = force_tls
    self.no_tls = no_tls
    self._smtp = _SMTPState()


SMTPMailer.__init__ = new_init
