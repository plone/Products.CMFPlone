from Products.SecureMailHost.SecureMailHost import SecureMailHost as Base

class MockMailHost(Base):
    """A MailHost that collects messages instead of sending them.

    Thanks to Rocky Burt for inspiration.
    """
    
    def __init__(self, id):
        Base.__init__(self, id, smtp_notls=True)
        self.reset()
    
    def reset(self):
        self.messages = []

    def send(self, message, mto=None, mfrom=None, subject=None, encode=None):
        self.messages.append(message)

    def secureSend(self, message, mto, mfrom, **kwargs):
        kwargs['debug'] = True
        result = Base.secureSend(self, message=message, mto=mto, mfrom=mfrom, **kwargs)
        self.messages.append(result)

    def validateSingleEmailAddress(self, address):
        return True # why not
