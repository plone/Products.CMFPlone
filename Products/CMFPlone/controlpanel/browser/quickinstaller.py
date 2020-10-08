from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import INonInstallable
from Products.Five.browser import BrowserView
from Products.GenericSetup import EXTENSION
from Products.GenericSetup.tool import UNKNOWN
from Products.statusmessages.interfaces import IStatusMessage
from plone.memoize import view
from zope.component import getAllUtilitiesRegisteredFor
import logging
import pkg_resources
import transaction


logger = logging.getLogger('Plone')


class InstallerView(BrowserView):
    """View on all contexts for installing and uninstalling products.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ps = getToolByName(self.context, 'portal_setup')
        self.errors = {}

    def is_profile_installed(self, profile_id):
        return self.ps.getLastVersionForProfile(profile_id) != UNKNOWN

    def is_product_installed(self, product_id):
        profile = self.get_install_profile(product_id, allow_hidden=True)
        if not profile:
            return False
        return self.is_profile_installed(profile['id'])

    def _install_profile_info(self, product_id):
        """List extension profile infos of a given product.
        """
        profiles = self.ps.listProfileInfo()
        # We are only interested in extension profiles for the product.
        # TODO Remove the manual Products.* check here. It is still needed.
        profiles = [
            prof for prof in profiles
            if prof['type'] == EXTENSION and (
                prof['product'] == product_id or
                prof['product'] == 'Products.%s' % product_id
            )
        ]
        return profiles

    def get_install_profiles(self, product_id):
        """List all installer profile ids of the given name.

        TODO Might be superfluous.
        """
        return [prof['id'] for prof in self._install_profile_info(product_id)]

    def _get_profile(self, product_id, name, strict=True, allow_hidden=False):
        """Return profile with given name.

        Also return None when no profiles are found at all.

        :param product_id: id of product/package.
            For example CMFPlone or plone.app.registry.
        :type product_id: string
        :param name: name of profile.
            Usually 'default' or 'uninstall'.
        :type name: string
        :param strict: When True, return None when name is not found.
            Otherwise fall back to the first profile.
        :type strict: boolean
        :param allow_hidden: Allow getting hidden profile.
            A non hidden profile is always preferred.
        :type allow_hidden: boolean
        :returns: True on success, False otherwise.
        :rtype: boolean
        """
        profiles = self._install_profile_info(product_id)
        if not profiles:
            return
        utils = getAllUtilitiesRegisteredFor(INonInstallable)
        hidden = []
        for util in utils:
            gnip = getattr(util, 'getNonInstallableProfiles', None)
            if gnip is None:
                continue
            hidden.extend(gnip())

        # We have prime candidates that we prefer, and have hidden candidates
        # in case allow_hidden is True.
        prime_candidates = []
        hidden_candidates = []
        for profile in profiles:
            profile_id = profile['id']
            profile_id_parts = profile_id.split(':')
            if len(profile_id_parts) != 2:
                logger.error("Profile with id '%s' is invalid." % profile_id)
                continue
            if allow_hidden and profile_id in hidden:
                if profile_id_parts[1] == name:
                    # This will especially be true for uninstall profiles,
                    # which are usually hidden.
                    return profile
                hidden_candidates.append(profile)
                continue
            if profile_id_parts[1] == name:
                return profile
            prime_candidates.append(profile)
        if strict:
            return
        if prime_candidates:
            # QI used to pick the first profile.
            # Return the first profile after all.
            return prime_candidates[0]
        if allow_hidden and hidden_candidates:
            # Return the first hidden profile.
            return hidden_candidates[0]

    def get_install_profile(self, product_id, allow_hidden=False):
        """Return the default install profile.

        :param product_id: id of product/package
        :type product_id: string
        :param allow_hidden: Allow getting otherwise hidden profile.
            In the UI this will be False, but you can set it to True in
            for example a call from plone.app.upgrade where you want to
            install a new core product, even though it is hidden for users.
        :type allow_hidden: boolean
        :returns: True on success, False otherwise.
        :rtype: boolean
        """
        return self._get_profile(product_id, 'default', strict=False,
                                 allow_hidden=allow_hidden)

    def get_uninstall_profile(self, product_id):
        """Return the uninstall profile.

        Note: not used yet.
        """
        return self._get_profile(
            product_id, 'uninstall', strict=True, allow_hidden=True)

    def is_product_installable(self, product_id, allow_hidden=False):
        """Does a product have an installation profile?

        :param allow_hidden: Allow installing otherwise hidden products.
            In the UI this will be False, but you can set it to True in
            for example a call from plone.app.upgrade where you want to
            install a new core product, even though it is hidden for users.
        :type allow_hidden: boolean
        :returns: True when product is installable, False otherwise.
        :rtype: boolean
        """
        if not allow_hidden:
            not_installable = []
            utils = getAllUtilitiesRegisteredFor(INonInstallable)
            for util in utils:
                gnip = getattr(util, 'getNonInstallableProducts', None)
                if gnip is None:
                    continue
                not_installable.extend(gnip())
            if product_id in not_installable:
                return False

        profile = self.get_install_profile(
            product_id, allow_hidden=allow_hidden)
        if profile is None:
            return
        try:
            self.ps.getProfileDependencyChain(profile['id'])
        except KeyError as e:
            # Don't show twice the same error: old install and profile
            # oldinstall is test in first in other methods we may have an extra
            # 'Products.' in the namespace.
            #
            # TODO:
            # 1. Make sense of the previous comment.
            # 2. Possibly remove the special case for 'Products'.
            # 3. Make sense of the next five lines: they remove 'Products.'
            #    when it is there, and add it when it is not???
            checkname = product_id
            if checkname.startswith('Products.'):
                checkname = checkname[9:]
            else:
                checkname = 'Products.' + checkname
            if checkname in self.errors:
                if self.errors[checkname]['value'] == e.args[0]:
                    return False
                # A new error is found, register it
                self.errors[product_id] = dict(
                    type=_(
                        "dependency_missing",
                        default="Missing dependency"
                    ),
                    value=e.args[0],
                    product_id=product_id
                )
            else:
                self.errors[product_id] = dict(
                    type=_(
                        "dependency_missing",
                        default="Missing dependency"
                    ),
                    value=e.args[0],
                    product_id=product_id
                )
            return False
        return True

    def get_product_version(self, product_id):
        """Return the version of the product (package).
        """
        try:
            dist = pkg_resources.get_distribution(product_id)
            return dist.version
        except pkg_resources.DistributionNotFound:
            if '.' in product_id:
                return ''
        # For CMFPlacefulWorkflow we need to try Products.CMFPlacefulWorkflow.
        return self.get_product_version('Products.' + product_id)

    def get_latest_upgrade_step(self, profile_id):
        """Get highest ordered upgrade step for profile.

        If anything errors out then go back to "old way" by returning
        'unknown'.
        """
        profile_version = UNKNOWN
        try:
            available = self.ps.listUpgrades(profile_id, True)
            if available:  # could return empty sequence
                latest = available[-1]
                profile_version = max(latest['dest'],
                                      key=pkg_resources.parse_version)
        except Exception:
            pass
        return profile_version

    def upgrade_info(self, product_id):
        """Returns upgrade info for a product.

        This is a dict with among others two booleans values, stating if
        an upgrade is required and available.

        :param product_id: id of product/package
        :type product_id: string
        :returns: dictionary with info about product
        :rtype: dict
        """
        available = self.is_product_installable(product_id, allow_hidden=True)
        if not available:
            return {}
        profile = self.get_install_profile(product_id, allow_hidden=True)
        if profile is None:
            # No GS profile, not supported.
            return {}
        profile_id = profile['id']
        if not self.is_profile_installed(profile_id):
            return {}
        profile_version = str(self.ps.getVersionForProfile(profile_id))
        if profile_version == 'latest':
            profile_version = self.get_latest_upgrade_step(profile_id)
        if profile_version == UNKNOWN:
            # If a profile doesn't have a metadata.xml use the package version.
            profile_version = self.get_product_version(product_id)
        installed_profile_version = self.ps.getLastVersionForProfile(
            profile_id)
        # getLastVersionForProfile returns the version as a tuple or unknown.
        if installed_profile_version != UNKNOWN:
            installed_profile_version = str(
                '.'.join(installed_profile_version))
        return dict(
            required=profile_version != installed_profile_version,
            available=len(self.ps.listUpgrades(profile_id)) > 0,
            hasProfile=True,  # TODO hasProfile is always True now.
            installedVersion=installed_profile_version,
            newVersion=profile_version,
        )

    def upgrade_product(self, product_id):
        """Run the upgrade steps for a product.

        Returns True on success, False otherwise.
        """
        profile = self.get_install_profile(product_id, allow_hidden=True)
        if profile is None:
            logger.error("Could not upgrade %s, no profile.", product_id)
            return False
        self.ps.upgradeProfile(profile['id'])
        return True

    def install_product(self, product_id, allow_hidden=False):
        """Install a product by name.

        :param product_id: id of product/package
        :type product_id: string
        :param allow_hidden: Allow installing otherwise hidden products.
            In the UI this will be False, but you can set it to True in
            for example a call from plone.app.upgrade where you want to
            install a new core product, even though it is hidden for users.
        :type allow_hidden: boolean
        :returns: True on success, False otherwise.
        :rtype: boolean
        """
        profile = self.get_install_profile(
            product_id, allow_hidden=allow_hidden)
        if not profile:
            logger.error("Could not install %s: no profile found.", product_id)
            # TODO Possibly raise an error.
            return False

        if self.is_product_installed(product_id):
            logger.error("Could not install %s: profile already installed.",
                         product_id)
            return False

        # Okay, actually install the profile.
        profile_id = profile['id']
        self.ps.runAllImportStepsFromProfile('profile-%s' % profile_id)

        if not self.is_profile_installed(profile_id):
            version = self.get_product_version(product_id)
            logger.warning('Profile %s has no metadata.xml version. Falling back '
                        'to package version %s', profile_id, version)
            self.ps.setLastVersionForProfile(profile_id, version)

        # No problems encountered.
        return True

    def uninstall_product(self, product_id):
        """Uninstall a product by name.

        Returns True on success, False otherwise.
        """
        profile = self.get_uninstall_profile(product_id)
        if not profile:
            logger.error("Could not uninstall %s: no uninstall profile "
                         "found.", product_id)
            return False

        self.ps.runAllImportStepsFromProfile(
            'profile-%s' % profile['id'])

        # Unmark the install profile.
        install_profile = self.get_install_profile(
            product_id, allow_hidden=True)
        if install_profile:
            self.ps.unsetLastVersionForProfile(install_profile['id'])
        return True


class ManageProductsView(InstallerView):
    """
    Activate and deactivate products in mass, and without weird
    permissions issues
    """

    def __call__(self):
        return self.index()

    @view.memoize
    def marshall_addons(self):
        addons = {}

        ignore_profiles = []
        ignore_products = []
        utils = getAllUtilitiesRegisteredFor(INonInstallable)
        for util in utils:
            ni_profiles = getattr(util, 'getNonInstallableProfiles', None)
            if ni_profiles is not None:
                ignore_profiles.extend(ni_profiles())
            ni_products = getattr(util, 'getNonInstallableProducts', None)
            if ni_products is not None:
                ignore_products.extend(ni_products())

        # Known profiles:
        profiles = self.ps.listProfileInfo()
        # Profiles that have upgrade steps (which may or may not have been
        # applied already).
        # profiles_with_upgrades = self.ps.listProfilesWithUpgrades()
        for profile in profiles:
            if profile['type'] != EXTENSION:
                continue

            pid = profile['id']
            if pid in ignore_profiles:
                continue
            pid_parts = pid.split(':')
            if len(pid_parts) != 2:
                logger.error("Profile with id '%s' is invalid." % pid)
            # Which package (product) is this from?
            product_id = profile['product']
            if product_id in ignore_products:
                continue
            profile_type = pid_parts[-1]
            if product_id not in addons:
                # get some basic information on the product
                installed = self.is_product_installed(product_id)
                upgrade_info = {}
                if installed:
                    upgrade_info = self.upgrade_info(product_id)
                elif not self.is_product_installable(product_id):
                    continue
                addons[product_id] = {
                    'id': product_id,
                    'version': self.get_product_version(product_id),
                    'title': product_id,
                    'description': '',
                    'upgrade_profiles': {},
                    'other_profiles': [],
                    'install_profile': None,
                    'install_profile_id': '',
                    'uninstall_profile': None,
                    'uninstall_profile_id': '',
                    'is_installed': installed,
                    'upgrade_info': upgrade_info,
                    'profile_type': profile_type,
                }
                # Add info on install and uninstall profile.
                product = addons[product_id]
                install_profile = self.get_install_profile(product_id)
                if install_profile is not None:
                    product['title'] = install_profile['title']
                    product['description'] = install_profile['description']
                    product['install_profile'] = install_profile
                    product['install_profile_id'] = install_profile['id']
                    product['profile_type'] = 'default'
                uninstall_profile = self.get_uninstall_profile(product_id)
                if uninstall_profile is not None:
                    product['uninstall_profile'] = uninstall_profile
                    product['uninstall_profile_id'] = uninstall_profile['id']
                    # Do not override profile_type.
                    if not product['profile_type']:
                        product['profile_type'] = 'uninstall'
            if profile['id'] in (product['install_profile_id'],
                                 product['uninstall_profile_id']):
                # Everything has been done.
                continue
            elif 'version' in profile:
                product['upgrade_profiles'][profile['version']] = profile
            else:
                product['other_profiles'].append(profile)
        return addons

    def get_addons(self, apply_filter=None, product_name=None):
        """
        100% based on generic setup profiles now.

        @filter:= 'installed': only products that are installed and not hidden
                  'upgrades': only products with upgrades
                  'available': products that are not installed bit
                               could be
                  'broken': uninstallable products with broken
                            dependencies

        @product_name:= a specific product id that you want info on. Do
                   not pass in the profile type, just the name

        XXX: I am pretty sure we don't want base profiles ...
        """
        addons = self.marshall_addons()
        filtered = {}
        if apply_filter == 'broken':
            all_broken = self.errors.values()
            for broken in all_broken:
                filtered[broken['product_id']] = broken
        else:
            for product_id, addon in addons.items():
                if product_name and addon['id'] != product_name:
                    continue

                installed = addon['is_installed']
                if apply_filter in ['installed', 'upgrades'] and not installed:
                    continue
                elif apply_filter == 'available':
                    if installed:
                        continue
                    # filter out upgrade profiles
                    if addon['profile_type'] != 'default':
                        continue
                elif apply_filter == 'upgrades':
                    upgrade_info = addon['upgrade_info']
                    if not upgrade_info.get('available'):
                        continue

                filtered[product_id] = addon

        return filtered

    def get_upgrades(self):
        """
        Return a list of products that have upgrades on tap
        """
        return self.get_addons(apply_filter='upgrades').values()

    def get_installed(self):
        return self.get_addons(apply_filter='installed').values()

    def get_available(self):
        return self.get_addons(apply_filter='available').values()

    def get_broken(self):
        return self.get_addons(apply_filter='broken').values()


class UpgradeProductsView(InstallerView):
    """
    Upgrade a product... or twenty
    """

    def __call__(self):
        products = self.request.get('prefs_reinstallProducts', None)
        if products:
            messages = IStatusMessage(self.request)
            for product_id in products:
                result = self.upgrade_product(product_id)
                if not result:
                    messages.addStatusMessage(
                        _('Error upgrading ${product}.',
                          mapping={'product': product_id}), type="error")
                    # Abort changes for all upgrades.
                    transaction.abort()
                    break
            else:
                messages.addStatusMessage(
                    _('Upgraded products.'), type="info")

        purl = getToolByName(self.context, 'portal_url')()
        self.request.response.redirect(purl + '/prefs_install_products_form')


class InstallProductsView(InstallerView):

    def __call__(self):
        product_id = self.request.get('install_product')
        if product_id:
            messages = IStatusMessage(self.request)
            msg_type = 'info'
            result = self.install_product(product_id)
            if result:
                msg = _('Installed ${product}!',
                        mapping={'product': product_id})
            else:
                # Only reason should be that between loading the page and
                # clicking to install a product, another user has already
                # installed this product.
                msg_type = 'error'
                msg = _('Failed to install ${product}.',
                        mapping={'product': product_id})
            messages.addStatusMessage(msg, type=msg_type)

        purl = getToolByName(self.context, 'portal_url')()
        self.request.response.redirect(purl + '/prefs_install_products_form')


class UninstallProductsView(InstallerView):

    def __call__(self):
        product_id = self.request.get('uninstall_product')
        if product_id:
            messages = IStatusMessage(self.request)
            try:
                result = self.uninstall_product(product_id)
            except Exception as e:
                logger.error("Could not uninstall %s: %s", product_id, e)
                msg_type = 'error'
                msg = _('Error uninstalling ${product}.', mapping={
                        'product': product_id})
            else:
                if result:
                    msg_type = 'info'
                    msg = _('Uninstalled ${product}.',
                            mapping={'product': product_id})
                else:
                    msg_type = 'error'
                    msg = _('Could not uninstall ${product}.',
                            mapping={'product': product_id})
            messages.addStatusMessage(msg, type=msg_type)

        purl = getToolByName(self.context, 'portal_url')()
        self.request.response.redirect(purl + '/prefs_install_products_form')
