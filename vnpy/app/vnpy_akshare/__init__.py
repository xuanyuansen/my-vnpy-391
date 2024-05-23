import importlib_metadata

from .akshare_datafeed import AkshareDatafeed as Datafeed


try:
    __version__ = importlib_metadata.version("vnpy_akshare")
except importlib_metadata.PackageNotFoundError:
    __version__ = "dev"