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


def freezeSecurityDeclarations(event):
    """Refuse changes to security declarations once Zope has started.

    After this, no code can make more modules, classes or types accessible
    from restricted code, for example with allow_module or allow_class.
    Zope may already have done this, in which case the freeze does nothing.
    """
    try:
        from AccessControl.SecurityInfo import check_dangerous_modules
        from AccessControl.SecurityInfo import freeze_security_declarations
    except ImportError:
        # AccessControl is too old.
        return
    # The standard dangerous modules are checked by the freeze.
    check_dangerous_modules({"plone.api.env", "plone.protect"})
    freeze_security_declarations()
