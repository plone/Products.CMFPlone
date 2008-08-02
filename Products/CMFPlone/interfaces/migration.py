from zope.interface import Interface

class IMigrationTool(Interface):
    """Handles migrations between Plone releases."""

    def getInstanceVersion():
        """The version this instance of Plone is on."""

    def setInstanceVersion(version):
        """The version this instance of Plone is on."""

    def knownVersions():
        """All known version ids, except current one and unsupported
           migration paths.
        """

    def unsupportedVersion():
        """Is the current instance version known to be a no longer supported
           version for migrations.
        """

    def getFileSystemVersion():
        """The version the filesystem code of Plone is on."""

    def getFSVersionTuple():
        """Returns tuple representing filesystem version."""

    def getInstanceVersionTuple():
        """Returns tuple representing instance version."""

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

    def getProductInfo():
        """Provide information about installed products for error reporting"""

    def upgrade(REQUEST=None, dry_run=None, swallow_errors=1):
        """Perform the upgrade."""
