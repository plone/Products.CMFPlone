from Products.CMFCore.utils import getToolByName

import logging


logger = logging.getLogger("Products.CMFPlone.controlpanel")


def migrate_to_email_login(context):
    pas = getToolByName(context, "acl_users")

    # We want the login name to be lowercase here.  This is new in
    # PAS.  Using 'manage_changeProperties' would change the login
    # names immediately, but we want to do that explicitly ourselves
    # and set the lowercase email address as login name, instead of
    # the lower case user id.
    # pas.manage_changeProperties(login_transform='lower')
    pas.login_transform = "lower"

    # Update the users.
    for user in pas.getUsers():
        if user is None:
            continue
        user_id = user.getUserId()
        email = user.getProperty("email", "")
        if email:
            login_name = pas.applyTransform(email)
            pas.updateLoginName(user_id, login_name)
        else:
            logger.warning("User %s has no email address.", user_id)


def migrate_from_email_login(context):
    pas = getToolByName(context, "acl_users")

    # Whether the login name is lowercase or not does not really
    # matter for this use case, but it may be better not to change
    # it at this point.

    # XXX
    pas.login_transform = ""

    # We do want to update the users.
    for user in pas.getUsers():
        if user is None:
            continue
        user_id = user.getUserId()
        # If we keep the transform to lowercase, then we must apply it
        # here as well, otherwise some users will not be able to
        # login, as their user id may be mixed or upper case.
        login_name = pas.applyTransform(user_id)
        pas.updateLoginName(user_id, login_name)
