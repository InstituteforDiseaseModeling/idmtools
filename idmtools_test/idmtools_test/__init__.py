import os
try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # Python < 3.8
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("idmtools-test")  # Use your actual package name
except PackageNotFoundError:
    # Package not installed, use fallback
    __version__ = "0.0.0+unknown"


current_directory = os.path.dirname(os.path.realpath(__file__))
COMMON_INPUT_PATH = os.path.join(current_directory, "inputs")
