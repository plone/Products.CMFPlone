from AccessControl import getSecurityManager
from AccessControl.Permissions import view as View
from collections import OrderedDict
from functools import cached_property
from importlib import import_module
from importlib.metadata import distribution
from importlib.metadata import PackageNotFoundError
from OFS.interfaces import IApplication
from plone.base.interfaces import IPloneSiteRoot
from plone.base.utils import get_installer
from plone.i18n.locales.interfaces import IContentLanguageAvailability
from plone.keyring.interfaces import IKeyManager
from plone.protect.authenticator import check as checkCSRF
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFCore.permissions import ManagePortal
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.factory import _TYPES_PROFILE
from Products.CMFPlone.factory import addPloneSite
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.GenericSetup.upgrade import normalize_version
from urllib import parse
from ZODB.broken import Broken
from zope.component import adapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.locales import LoadLocaleError
from zope.i18n.locales import locales
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import IRequest
from zope.schema.interfaces import IVocabularyFactory
from ZPublisher.BaseRequest import DefaultPublishTraverse

import logging


try:
    distribution("plone.volto")
    HAS_VOLTO = True
except PackageNotFoundError:
    HAS_VOLTO = False
try:
    distribution("plone.app.caching")
    HAS_CACHING = True
except PackageNotFoundError:
    HAS_CACHING = False
try:
    distribution("plone.app.upgrade")
    HAS_UPGRADE = True
except PackageNotFoundError:
    HAS_UPGRADE = False
LOGGER = logging.getLogger("Products.CMFPlone")


@adapter(IApplication, IRequest)
class AppTraverser(DefaultPublishTraverse):
    def publishTraverse(self, request, name):
        if name == "index_html":
            view = queryMultiAdapter(
                (self.context, request), Interface, "plone-overview"
            )
            if view is not None:
                return view
        return DefaultPublishTraverse.publishTraverse(self, request, name)


class Overview(BrowserView):
    def sites(self, root=None):
        if root is None:
            root = self.context

        result = []
        secman = getSecurityManager()
        candidates = (obj for obj in root.values() if not isinstance(obj, Broken))
        for obj in candidates:
            if obj.meta_type == "Folder":
                result = result + self.sites(obj)
            elif IPloneSiteRoot.providedBy(obj):
                if secman.checkPermission(View, obj):
                    result.append(obj)
            elif obj.getId() in getattr(root, "_mount_points", {}):
                result.extend(self.sites(root=obj))
        return result

    def outdated(self, obj):
        # Try to pick the portal_migration as an attribute
        # (Plone 5 unmigrated site root) or as an item
        mig = getattr(obj, "portal_migration", None) or obj.get(
            "portal_migration", None
        )
        if mig is not None:
            return mig.needUpgrading()
        return False

    def can_manage(self):
        secman = getSecurityManager()
        return secman.checkPermission(ManagePortal, self.context)

    def upgrade_url(self, site, can_manage=None):
        if can_manage is None:
            can_manage = self.can_manage()
        if can_manage:
            return site.absolute_url() + "/@@plone-upgrade"
        else:
            return self.context.absolute_url() + "/@@plone-root-login"


class RootLoginRedirect(BrowserView):
    """@@plone-root-login

    This view of the Zope root forces authentication via the root
    acl_users and then redirects elsewhere.
    """

    def __call__(self, came_from=None):
        if came_from is not None:
            # see if this is a relative url or an absolute
            if len(parse.urlparse(came_from)[1]) == 0:
                # No host specified, so url is relative.  Get an absolute url.
                # Note: '\\domain.org' is not recognised as host,
                # which is good.
                came_from = parse.urljoin(
                    self.context.absolute_url() + "/",
                    came_from,
                )
            elif not came_from.startswith(self.context.absolute_url()):
                # Note: we cannot use portal_url.isURLInPortal here, because we
                # are not in a Plone portal, but in the Zope root.
                came_from = None
        if came_from is None:
            came_from = self.context.absolute_url()
        self.request.response.redirect(came_from)


class RootLogout(BrowserView):
    """@@plone-root-logout"""

    logout = ViewPageTemplateFile("templates/plone-admin-logged-out.pt")

    def __call__(self):
        response = self.request.response
        realm = response.realm
        response.setStatus(401)
        response.setHeader("WWW-Authenticate", 'basic realm="%s"' % realm, 1)
        response.setBody(self.logout())
        return


class FrontPage(BrowserView):
    index = ViewPageTemplateFile("templates/plone-frontpage.pt")


class AddPloneSite(BrowserView):
    @property
    def default_extension_profiles(self):
        # Profiles that are installed by default,
        # but can be removed later.
        profiles = [_TYPES_PROFILE]
        if HAS_CACHING:
            profiles.append("plone.app.caching:default")
        profiles.append("plonetheme.barceloneta:default")
        return profiles

    def browser_language(self):
        language = "en"
        pl = IUserPreferredLanguages(self.request)
        if pl is not None:
            languages = pl.getPreferredLanguages()
            for httplang in languages:
                parts = (httplang.split("-") + [None, None])[:3]
                if parts[0] == parts[1]:
                    # Avoid creating a country code for simple languages codes
                    parts = [parts[0], None, None]
                try:
                    locale = locales.getLocale(*parts)
                    language = locale.getLocaleID().replace("_", "-").lower()
                    break
                except LoadLocaleError:
                    # Just try the next combination
                    pass
        return language

    def grouped_languages(self, default="en"):
        util = queryUtility(IContentLanguageAvailability)
        available = util.getLanguages(combined=True)
        languages = dict(util.getLanguageListing())

        # Group country specific versions by language
        grouped = OrderedDict()
        for langcode, data in available.items():
            lang = langcode.split("-")[0]
            language = languages.get(lang, lang)  # Label

            struct = grouped.get(lang, {"label": language, "languages": []})

            langs = struct["languages"]
            langs.append(
                {
                    "langcode": langcode,
                    "label": data.get("native", data.get("name")),
                }
            )

            grouped[lang] = struct

        # Sort list by language, next by country
        data = sorted(grouped.values(), key=lambda k: k["label"])
        for item in data:
            item["languages"] = sorted(
                item["languages"], key=lambda k: k["label"].lower()
            )
        return data

    def timezones(self):
        tz_vocab = getUtility(
            IVocabularyFactory, "plone.app.vocabularies.CommonTimezones"
        )(self.context)

        grouped = OrderedDict()
        tz_values = [it.value for it in tz_vocab]
        for value in tz_values:
            split = value.split("/")
            group = split.pop(0)
            label = "/".join(split)

            entries = grouped.get(group, [])
            entries.append({"label": label or group, "value": value})
            grouped[group] = entries

        return grouped

    def __call__(self):
        context = self.context
        form = self.request.form
        submitted = form.get("form.submitted", False)
        if submitted:
            site_id = form.get("site_id", "Plone")

            # CSRF protect. DO NOT use auto CSRF protection for adding a site
            alsoProvides(self.request, IDisableCSRFProtection)

            # check if keyring is installed on root, disable CSRF protection
            # if it is because it is not installed until a plone site
            # is created
            if queryUtility(IKeyManager) is None:
                LOGGER.info("CSRF protection disabled on initial site " "creation")
            else:
                # we have a keymanager, check csrf protection manually now
                checkCSRF(self.request)

            site = addPloneSite(
                context,
                site_id,
                title=form.get("title", ""),
                profile_id=_DEFAULT_PROFILE,
                extension_ids=self.default_extension_profiles,
                default_language=form.get("default_language", "en"),
                portal_timezone=form.get("portal_timezone", "UTC"),
            )
            self.request.response.redirect(site.absolute_url())
            return ""

        return self.index()


class Upgrade(BrowserView):
    has_upgrade = HAS_UPGRADE

    def upgrades(self):
        pm = getattr(self.context, "portal_migration")
        return pm.listUpgrades()

    @cached_property
    def missing_packages(self):
        """Get list of missing packages that were installed in GS.

        Main use case:

        * Create a Product.CMFPlone 6.0 site.
        * Upgrade the code to Products.CMFPlone 6.1.
        * Now the plone.app.discussion package is missing.
          This will give problems, because its GS profile was installed
          by default in 6.0.

        Beware of false positives.  For example when upgrading from Plone 5.2,
        CMFFormController will be missing, but we have code in plone.app.upgrade
        to properly clean this up. So we should not bother the admin with this.
        """
        setup = getattr(self.context, "portal_setup")
        installed = sorted(
            {x.split(":")[0] for x in setup._profile_upgrade_versions.keys()}
        )
        ignore = ["Products.CMFFormController"]
        missing = []
        for package in installed:
            if package in ignore:
                continue
            try:
                distribution(package)
            except PackageNotFoundError:
                try:
                    # profiles can live in submodules of packages.
                    # check if we can import the module namespace
                    import_module(package)
                except ModuleNotFoundError:
                    missing.append(package)
        return missing

    def versions(self):
        pm = getattr(self.context, "portal_migration")
        result = {}
        result["instance"] = pm.getInstanceVersion()
        result["fs"] = pm.getFileSystemVersion()
        result["equal"] = result["instance"] == result["fs"]
        instance_version = normalize_version(result["instance"])
        fs_version = normalize_version(result["fs"])
        result["instance_gt"] = instance_version > fs_version
        result["instance_lt"] = instance_version < fs_version
        result["corelist"] = pm.coreVersions()
        return result

    def __call__(self):
        form = self.request.form
        submitted = form.get("form.submitted", False)
        if submitted:
            # CSRF protect. DO NOT use auto CSRF protection for upgrading sites
            alsoProvides(self.request, IDisableCSRFProtection)

            pm = getattr(self.context, "portal_migration")
            report = pm.upgrade(
                REQUEST=self.request,
                dry_run=form.get("dry_run", False),
            )
            return self.index(
                report=report,
            )

        return self.index()

    def can_migrate_to_volto(self):
        if not HAS_VOLTO:
            return False
        pm = getattr(self.context, "portal_migration")
        if pm.getInstanceVersion() < "6005":
            return False
        try:
            from plone.volto.browser import migrate_to_volto  # noqa: F401
        except ImportError:
            return False
        installer = get_installer(self.context, self.request)
        return not installer.is_product_installed("plone.volto")
