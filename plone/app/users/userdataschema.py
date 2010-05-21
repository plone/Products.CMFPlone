from AccessControl import Unauthorized

from zope.interface import Interface, implements
from zope import schema
from zope.component import getUtility
from zope.schema import ValidationError

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.exceptions import EmailAddressInvalid
from Products.CMFDefault.formlib.schema import FileUpload
from Products.CMFPlone import PloneMessageFactory as _


class IUserDataSchemaProvider(Interface):
    """
    """

    def getSchema():
        """
        """


class UserDataSchemaProvider(object):
    implements(IUserDataSchemaProvider)

    def getSchema(self):
        """
        """
        return IUserDataSchema


class CantChangeEmailError(ValidationError):
    __doc__ = _('message_email_cannot_change',
                u"Sorry, you are not allowed to change your email address.")


class EmailInUseError(ValidationError):
    __doc__ = _('message_email_in_use',
                u"The email address you selected is already in use "
                  "or is not valid as login name. Please choose "
                  "another.")


def checkEmailAddress(value):
    portal = getUtility(ISiteRoot)

    reg_tool = getToolByName(portal, 'portal_registration')
    if value and reg_tool.isValidEmail(value):
        pass
    else:
        raise EmailAddressInvalid

    # If emails are used as logins, ensure that the address fits all
    # constraints.
    props = getToolByName(portal, 'portal_properties').site_properties
    if props.getProperty('use_email_as_login'):
        try:
            id_allowed = reg_tool.isMemberIdAllowed(value)
        except Unauthorized:
            raise CantChangeEmailError
        else:
            if not id_allowed:
                # Keeping your email the same (which happens when you
                # change something else on the personalize form) or
                # changing it back to your login name, is fine.
                membership = getToolByName(portal, 'portal_membership')
                if not membership.isAnonymousUser():
                    member = membership.getAuthenticatedMember()
                    if value in (member.getId(), member.getUserName()):
                        return True
                raise EmailInUseError
    return True


class IUserDataSchema(Interface):
    """
    """

    fullname = schema.TextLine(
        title=_(u'label_full_name', default=u'Full Name'),
        description=u'',
        required=False)

    email = schema.ASCIILine(
        title=_(u'label_email', default=u'E-mail'),
        description=u'',
        required=True,
        constraint=checkEmailAddress)

    home_page = schema.TextLine(
        title=_(u'label_homepage', default=u'Home page'),
        description=_(u'help_homepage',
                      default=u"The URL for your external home page, "
                      "if you have one."),
        required=False)

    description = schema.Text(
        title=_(u'label_biography', default=u'Biography'),
        description=_(u'help_biography',
                      default=u"A short overview of who you are and what you "
                      "do. Will be displayed on your author page, linked "
                      "from the items you create."),
        required=False)

    location = schema.TextLine(
        title=_(u'label_location', default=u'Location'),
        description=_(u'help_location',
                      default=u"Your location - either city and "
                      "country - or in a company setting, where "
                      "your office is located."),
        required=False)

    portrait = FileUpload(title=_(u'label_portrait', default=u'Portrait'),
        description=_(u'help_portrait',
                      default=u'To add or change the portrait: click the '
                      '"Browse" button; select a picture of yourself. '
                      'Recommended image size is 75 pixels wide by 100 '
                      'pixels tall.'),
        required=False)

    pdelete = schema.Bool(
        title=_(u'label_delete_portrait', default=u'Delete Portrait'),
        description=u'',
        required=False)
