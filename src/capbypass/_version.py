"""Installed version of the package, read from its distribution metadata.

The publish workflow writes the release version into pyproject.toml before the
build, so the metadata of an installed wheel is the single source of truth.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("capbypass-sdk")
except PackageNotFoundError:  # running from a source tree that is not installed
    __version__ = "unknown"
