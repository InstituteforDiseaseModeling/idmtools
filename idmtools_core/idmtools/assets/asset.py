import io

import os
from dataclasses import dataclass, field, InitVar
from io import BytesIO
from logging import getLogger, DEBUG
from typing import TypeVar, Union, List, Callable, Any, Optional, Generator, BinaryIO

import backoff
import requests
from tqdm import tqdm

from idmtools.utils.hashing import calculate_md5, calculate_md5_stream

logger = getLogger(__name__)


@dataclass(repr=False)
class Asset:
    """
    A class representing an asset. An asset can either be related to a physical
    asset present on the computer or directly specified by a filename and content.

    Args:
        absolute_path: The absolute path of the asset. Optional if **filename** and **content** are given.
        relative_path:  The relative path (compared to the simulation root folder).
        filename: Name of the file. Optional if **absolute_path** is given.
        content: The content of the file. Optional if **absolute_path** is given.
        checksum: Optional. Useful in systems that allow single upload based on checksums and retrieving from those
            systems

            Note: we add this to allow systems who provide asset caching by MD5 opportunity to avoid re-uploading assets
    """

    absolute_path: Optional[str] = field(default=None)
    relative_path: Optional[str] = field(default=None)
    filename: Optional[str] = field(default=None)
    content: InitVar[Any] = None
    _content: bytes = field(default=None, init=False)
    _length: Optional[int] = field(default=None)
    persisted: bool = field(default=False)
    handler: Callable = field(default=str, metadata=dict(exclude_from_metadata=True))
    download_generator_hook: Callable = field(default=None, metadata=dict(exclude_from_metadata=True))
    checksum: InitVar[Any] = None
    _checksum: Optional[str] = field(default=None)

    def __post_init__(self, content, checksum):
        self._checksum = checksum if not isinstance(checksum, property) else None
        self.content = content
        self.filename = self.filename or (os.path.basename(self.absolute_path) if self.absolute_path else None)
        # populate absolute path for conditions where user does not supply info
        if not self._checksum and not self.content and not self.absolute_path and self.filename:
            self.absolute_path = os.path.abspath(self.filename)

        if self.absolute_path and not os.path.exists(self.absolute_path):
            raise FileNotFoundError(f"Cannot find specified asset: {self.absolute_path}")
        elif not self.absolute_path and (not self.filename or (self.filename and not self._checksum and not self.content)):
            raise ValueError("Impossible to create the asset without either absolute path, filename and content, or filename and checksum!")

    def __repr__(self):
        return f"<Asset: {os.path.join(self.relative_path, self.filename)} from {self.absolute_path}>"

    @property
    def checksum(self):
        """
        Returns:
            None.
        """
        return self._checksum

    @checksum.setter
    def checksum(self, checksum):
        self._checksum = checksum

    @property
    def extension(self):
        return os.path.splitext(self.filename)[1].lstrip('.').lower()

    @property
    def relative_path(self):
        return self._relative_path or ""

    @relative_path.setter
    def relative_path(self, relative_path):
        self._relative_path = relative_path.strip(" \\/") if not isinstance(relative_path, property) and relative_path else None

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
        if not self._content and self.absolute_path:
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
    def __eq__(self, other):
        return self.__key() == other.__key()

    def __key(self):
        if self.absolute_path:
            return self.absolute_path

        if self.filename and self.relative_path:
            return self.filename, self.relative_path

        return self._content, self.filename

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
        if progress:
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
            path: Path to write to. If it is a directory, the asset filename will be added to it

        Returns:
            None
        """

        if os.path.isdir(dest):
            if self.relative_path:
                path = os.path.join(dest, self.relative_path, self.filename)
            else:
                path = os.path.join(dest, self.filename)
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
        Calculate checksum on asset
        Returns:

        """
        if not self._checksum:
            if self.absolute_path:
                self._checksum = calculate_md5(self.absolute_path)
            elif self.content:
                self._checksum = calculate_md5_stream(io.BytesIO(self.content.encode('utf-8')) if isinstance(self.content, str) else io.BytesIO(self.content) )
        return self._checksum


TAsset = TypeVar("TAsset", bound=Asset)
# Assets types
TAssetList = List[TAsset]

# Filters types
TAssetFilter = Union[Callable[[TAsset], bool], Callable]
TAssetFilterList = List[TAssetFilter]
