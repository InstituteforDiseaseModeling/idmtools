import io
import os
from dataclasses import dataclass, field, InitVar
from io import BytesIO
from logging import getLogger, DEBUG
from pathlib import PosixPath
from typing import TypeVar, Union, List, Callable, Any, Optional, Generator, BinaryIO
import backoff
import requests
from idmtools import IdmConfigParser
from idmtools.utils.hashing import calculate_md5, calculate_md5_stream

logger = getLogger(__name__)


@dataclass(repr=False)
class Asset:
    """
    A class representing an asset. An asset can either be related to a physical
    asset present on the computer or directly specified by a filename and content.

    """

    #: The absolute path of the asset. Optional if **filename** and **content** are given.
    absolute_path: Optional[str] = field(default=None)
    #: The relative path (compared to the simulation root folder).
    relative_path: Optional[str] = field(default=None)
    #: Name of the file. Optional if **absolute_path** is given.
    filename: Optional[str] = field(default=None)
    #: The content of the file. Optional if **absolute_path** is given.
    content: InitVar[Any] = None
    _content: bytes = field(default=None, init=False)
    _length: Optional[int] = field(default=None, init=False)
    #: Persisted tracks if item has been saved
    persisted: bool = field(default=False)
    #: Handler to api
    handler: Callable = field(default=str, metadata=dict(exclude_from_metadata=True))
    #: Hook to allow downloading from platform
    download_generator_hook: Callable = field(default=None, metadata=dict(exclude_from_metadata=True))
    #: Checksum of asset. Only required for existing assets
    checksum: InitVar[Any] = None
    _checksum: Optional[str] = field(default=None, init=False)

    def __post_init__(self, content, checksum):
        # Cache of our assset key
        self._key = None
        self._content = None if isinstance(content, property) else content
        self._checksum = checksum if not isinstance(checksum, property) else None
        self.filename = self.filename or (os.path.basename(self.absolute_path) if self.absolute_path else None)
        # populate absolute path for conditions where user does not supply info
        if not self._checksum and self._content is None and not self.absolute_path and self.filename and not self.persisted:
            # try relative path
            if self.relative_path and os.path.exists(self.short_remote_path()):
                self.absolute_path = os.path.abspath(self.short_remote_path())
            else:
                self.absolute_path = os.path.abspath(self.filename)
        if self.absolute_path and self._content is not None:
            raise ValueError("Absolute Path and Content are mutually exclusive. Please provide only one of the options")
        elif self.absolute_path and not os.path.exists(self.absolute_path):
            raise FileNotFoundError(f"Cannot find specified asset: {self.absolute_path}")
        elif self.absolute_path and os.path.isdir(self.absolute_path) and not self.persisted:
            raise ValueError("Asset cannot be a directory!")
        elif not self.absolute_path and (not self.filename or (self.filename and not self._checksum and self._content is None and not self.persisted)):
            raise ValueError("Impossible to create the asset without either absolute path, filename and content, or filename and checksum!")

    def __repr__(self):
        return f"<Asset: {os.path.join(self.relative_path, self.filename)} from {self.absolute_path}>"

    @property
    def checksum(self):
        """

        Returns checksum of object. This will return None unless the user has provided checksum or called calculate checksum to avoid
        computation. If you need to guarantee a checksum value, call calculate_checksum beforehand
        Returns:
            Checksum
        """
        return self._checksum

    @checksum.setter
    def checksum(self, checksum):
        self._checksum = checksum

    @property
    def extension(self):
        return os.path.splitext(self.filename)[1].lstrip('.').lower()

    @property
    def filename(self):
        return self._filename or ""

    @filename.setter
    def filename(self, filename):
        self._filename = filename if not isinstance(filename, property) and filename else None
        self._key = None

    @property
    def relative_path(self):
        return self._relative_path or ""

    @relative_path.setter
    def relative_path(self, relative_path):
        self._relative_path = relative_path.strip(" \\/") if not isinstance(relative_path, property) and relative_path else None
        self._key = None

    @property
    def bytes(self):
        if isinstance(self.content, bytes):
            return self.content
        return str.encode(self.handler(self.content))

    @property
    def length(self):
        if self._length is None:
            self._length = len(self.content)
        return self._length

    @length.setter
    def length(self, new_length):
        self._length = new_length

    @property
    def content(self):
        """
        Returns:
            The content of the file, either from the content attribute or by opening the absolute path.
        """
        if self._content is None and self.absolute_path:
            with open(self.absolute_path, "rb") as fp:
                self._content = fp.read()

        elif self.download_generator_hook:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Fetching {self.filename} content from platform")
            self._content = self.download_stream().getvalue()

        return self._content

    @content.setter
    def content(self, content):
        self._content = None if isinstance(content, property) else content
        # Reset checksum to None until requested
        if self._checksum:
            self._checksum = None

    # region Equality and Hashing
    def __eq__(self, other: 'Asset'):
        return self.__key() == other.__key()

    def deep_equals(self, other: 'Asset') -> bool:
        """
        Performs a deep comparison of assets, including contents

        Args:
            other: Other asset to compare

        Returns:
            True if filename, relative path, and contents are equal, otherwise false
        """
        if self.filename == other.filename and self.relative_path == other.relative_path:
            return self.calculate_checksum() == other.calculate_checksum()
        return False

    def __key(self):
        # We only care to check if filename and relative path is same. Goal here is not identical check but rather that
        # two files don't exist in same remote path
        if self._key is None:
            self._key = self.filename, self.relative_path
        return self._key

    def __hash__(self):
        return hash(self.__key())
    # endregion

    def download_generator(self) -> Generator[bytearray, None, None]:
        """
        A Download Generator that returns chunks of bytes from the file


        Returns:
            Generator of bytearray
        """
        if self.download_generator_hook:
            return self.download_generator_hook()
        else:
            raise ValueError("To be able to download, the Asset needs to be fetched from a platform object")

    def download_stream(self) -> BytesIO:
        """
        Get a bytes IO stream of the asset

        Returns:
            BytesIO of the Asset
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Download {self.filename} to stream")
        io = BytesIO()
        self.__write_download_generator_to_stream(io)
        return io

    @backoff.on_exception(backoff.expo, (requests.exceptions.Timeout, requests.exceptions.ConnectionError), max_tries=8)
    def __write_download_generator_to_stream(self, stream: BinaryIO, progress: bool = False):
        """
        Write the download generator to another stream

        Args:
            stream:
            progress:

        Returns:

        """
        gen = self.download_generator()
        if progress and not IdmConfigParser.is_progress_bar_disabled():
            from tqdm import tqdm
            gen = tqdm(gen, total=self.length)

        try:
            for chunk in gen:
                if progress:
                    gen.update(len(chunk))
                stream.write(chunk)
        finally:  # close progress if we have it open
            if progress:
                gen.close()

    def download_to_path(self, dest: str, force: bool = False):
        """
        Download an asset to path. This requires loadings the object through the platofrm

        Args:
            dest: Path to write to. If it is a directory, the asset filename will be added to it
            force: Force download even if file exists

        Returns:
            None
        """

        if os.path.isdir(dest):
            path = os.path.join(dest, self.short_remote_path())
            path = path.replace("\\", os.path.sep)
            os.makedirs(os.path.dirname(path), exist_ok=True)
        else:
            path = dest

        if not os.path.exists(path) or force:
            with open(path, 'wb') as out:
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Download {self.filename} to {path}")
                self.__write_download_generator_to_stream(out)

    def calculate_checksum(self) -> str:
        """
        Calculate checksum on asset. If previous checksum was calculated, that value will be returned

        Returns:
            Checksum string
        """
        if not self._checksum:
            if self.absolute_path:
                self._checksum = calculate_md5(self.absolute_path)
            elif self.content is not None:
                self._checksum = calculate_md5_stream(io.BytesIO(self.bytes))
        return self._checksum

    def short_remote_path(self) -> str:
        """
        Returns the short remote path. This is the join of the relative path and filename

        Returns:
            Remote Path + Filename
        """

        if self.relative_path:
            path = PosixPath(self.relative_path).joinpath(self.filename)
        else:
            path = PosixPath(self.filename)
        return str(path)


TAsset = TypeVar("TAsset", bound=Asset)
# Assets types
TAssetList = List[TAsset]

# Filters types
TAssetFilter = Union[Callable[[TAsset], bool], Callable]
TAssetFilterList = List[TAssetFilter]
