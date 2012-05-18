import logging
import transaction
from transaction._transaction import Status

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
