from importlib.metadata import distribution
from importlib.metadata import PackageNotFoundError


HAS_ZSERVER = True
try:
    dist = distribution("ZServer")
except PackageNotFoundError:
    HAS_ZSERVER = False

NullResource = None
