from zope.interface import Interface, Attribute


class IPasswordResetToolView(Interface):
    """ BrowserView with utility methods """

    def encode_mail_header(text):
        """ Encodes text into correctly encoded email header """

    def encoded_mail_sender():
        """ returns encoded version of Portal name <portal_email> """

    def registered_notify_subject():
        """ returns encoded version of registered notify template subject line """

    def mail_password_subject():
        """ returns encoded version of mail password template subject line """


class IPWResetTool(Interface):
    """Defines an interface for a tool that provides a facility to
    reset forgotten passwords.

    This interface is rather sparse, but sufficient to describe the
    task. (In this manner we void being dependant on a specific
    process) The details of the process are in the implementation,
    where they belong."""

    id = Attribute('id', 'Must be set to "portal_password_reset"')

    def requestReset(userid):
        """Ask the system to start the password reset procedure for
        user 'userid'.

        Returns the random string that must be used to reset the
        password."""

    def resetPassword(userid, randomstring, password):
        """Set the password (in 'password') for the user who maps to
        the string in 'randomstring'. The 'userid' parameter is provided
        in case extra authentication is needed."""
