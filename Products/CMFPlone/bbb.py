import pkg_resources


HAS_ZSERVER = True
try:
    dist = pkg_resources.get_distribution("ZServer")
except pkg_resources.DistributionNotFound:
    HAS_ZSERVER = False

NullResource = None
