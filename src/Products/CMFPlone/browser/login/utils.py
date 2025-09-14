from DateTime import DateTime
from DateTime.interfaces import SyntaxError as DateTimeSyntaxError

import logging


logger = logging.getLogger(__name__)


def has_logged_in(login_time):
    """Is this a valid login time?

    The login time for new users is set to January 1, 2000.
    If that is the login time, the user has not logged in yet.
    """
    if not login_time:
        return False
    if not isinstance(login_time, DateTime):
        try:
            login_time = DateTime(login_time)
        except DateTimeSyntaxError:
            # https://github.com/plone/Products.CMFPlone/issues/3656
            logger.warning("%r is not a valid login_time.", login_time)
            return False
    # We used to compare login_time with DateTime('2000/01/01'),
    # but it may have a timezone: I have seen both UTC and GTM+1.
    # So compare only the date part.
    return login_time.Date() != "2000/01/01"
