from plone.base.interfaces import IReorderedEvent
from plone.base.interfaces import ISiteManagerCreatedEvent
from plone.base.utils import get_installer
from zope.interface import implementer
from zope.interface.interfaces import ObjectEvent


@implementer(ISiteManagerCreatedEvent)
class SiteManagerCreatedEvent(ObjectEvent):
    pass


@implementer(IReorderedEvent)
class ReorderedEvent(ObjectEvent):
    pass


def profileImportedEventHandler(event):
    """
    When a profile is imported with the keyword "latest", it needs to
    be reconfigured with the actual number.
    """
    profile_id = event.profile_id
    if profile_id is None:
        return
    profile_id = profile_id.replace("profile-", "")
    gs = event.tool
    installed_version = gs.getLastVersionForProfile(profile_id)
    if installed_version == ("latest",):
        qi = get_installer(gs, gs.REQUEST)
        actual_version = qi.get_latest_upgrade_step(profile_id)
        gs.setLastVersionForProfile(profile_id, actual_version)


def removeBase(event):
    """Make Zope not to inject a <base> tag into the returned HTML
    https://dev.plone.org/ticket/13705
    """
    event.request.response.base = None


def _checkSecurityDeclarations(event):
    """Refuse changes to security declarations once Zope has started.

    After this, no code can make more modules, classes or types accessible
    from restricted code, for example with allow_module or allow_class.

    This needs AccessControl 7.6+.  Plone 6.2 pins AccessControl 7.7 for
    Python 3.11+, but 7.4 for Python 3.10, because 7.6 dropped 3.10.
    So we catch an ImportError.
    """
    try:
        from AccessControl.SecurityInfo import check_dangerous_modules
        from AccessControl.SecurityInfo import freeze_security_declarations
    except ImportError:
        # AccessControl is too old.
        # TODO Remove try/except once we require AccessControl 7.6+.
        return

    # The standard dangerous modules are checked by the freeze.
    # We check a few extra ones that are not relevant for Zope.
    check_dangerous_modules({"plone.api.env", "plone.protect"})

    # Zope 6.3 will already call freeze_security_declarations.
    # In that case our own call will do nothing, which is fine.
    # As long as we still use Zope 6.2, we should keep this line.
    # TODO Remove once we use Zope 6.3.
    freeze_security_declarations()
