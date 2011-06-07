from zope.interface import Interface


class IMigrationTool(Interface):
    """Handles migrations between Plone releases."""

    def getInstanceVersion():
        """The version this instance of Plone is on."""

    def setInstanceVersion(version):
        """The version this instance of Plone is on."""

    def getFileSystemVersion():
        """The version the filesystem code of Plone is on."""

    def needUpgrading():
        """Need upgrading?"""

    def coreVersions():
        """Useful core version information."""

    def coreVersionsList():
        """Useful core version information."""

    def needUpdateRole():
        """Do roles need to be updated?"""

    def needRecatalog():
        """Does this thing now need recataloging?"""

    def upgrade(REQUEST=None, dry_run=None, swallow_errors=1):
        """Perform the upgrade."""
