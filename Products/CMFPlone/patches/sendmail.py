from plone.base.interfaces import IMailSchema
from plone.registry.interfaces import IRegistry
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

    old_mailer = getattr(SMTPMailer, "vote", None) is None
    if old_mailer:
        SMTPMailer.send = catchAllExceptions(SMTPMailer.send)


def mail_settings_wrapper(func):
    def wrapper(self, **kwargs):
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        kwargs["hostname"] = mail_settings.smtp_host
        kwargs["port"] = mail_settings.smtp_port
        kwargs["username"] = mail_settings.smtp_userid
        kwargs["password"] = mail_settings.smtp_pass
        return func(self, **kwargs)

    return wrapper

SMTPMailer.__init__ = mail_settings_wrapper(SMTPMailer.__init__)
