# -*- coding: utf-8 -*-
from zope.interface import Interface


class INonInstallable(Interface):

    def getNonInstallableProfiles():
        """Returns a list of profiles that should not be available for
           installation at portal creation time.

           The usual use-case is to prevent extension profiles from showing up,
           that will be installed as part of the site creation anyways.
        """

    def getNonInstallableProducts():
        """Returns a list of products that should not be available for
           installation.

        This used to be in CMFQuickInstallerTool.
        """
