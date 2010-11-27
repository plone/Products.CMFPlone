import logging

log = logging.getLogger("MailDataManager")


def catchAllExceptions(func):
    def _catch(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log.exception(e)
    return _catch


def applyPatches():
    from zope.sendmail.mailer import SMTPMailer
    old_mailer = getattr(SMTPMailer, 'vote', None) is None
    if old_mailer:
        SMTPMailer.send = catchAllExceptions(SMTPMailer.send)
