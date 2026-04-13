"""iidmtools_cli version definition file."""
try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # Python < 3.8
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("idmtools-cli")  # Use your actual package name
except PackageNotFoundError:
    # Package not installed, use fallback
    __version__ = "0.0.0+unknown"
