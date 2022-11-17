"""
IPlatformAssetCollectionOperations defines asset collection operations interface.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from logging import DEBUG, getLogger
from typing import Any, List, Type, NoReturn, TYPE_CHECKING
from idmtools.assets import AssetCollection
from idmtools.core import CacheEnabled
from idmtools.entities.iplatform_ops.utils import batch_create_items
from idmtools.registry.functions import FunctionPluginManager

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform
logger = getLogger(__name__)


@dataclass
class IPlatformAssetCollectionOperations(CacheEnabled, ABC):
    """
    IPlatformAssetCollectionOperations defines asset collection operations interface.
    """
    platform: 'IPlatform'  # noqa: F821
    platform_type: Type

    def pre_create(self, asset_collection: AssetCollection, **kwargs) -> NoReturn:
        """
        Run the platform/AssetCollection post creation events.

        Args:
            asset_collection: AssetCollection to run post-creation events
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            NoReturn
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling idmtools_platform_pre_create_item")
        FunctionPluginManager.instance().hook.idmtools_platform_pre_create_item(item=asset_collection, kwargs=kwargs)
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling pre_creation")
        asset_collection.pre_creation(self.platform)

    def post_create(self, asset_collection: AssetCollection, **kwargs) -> NoReturn:
        """
        Run the platform/AssetCollection post creation events.

        Args:
            asset_collection: AssetCollection to run post-creation events
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            NoReturn
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling idmtools_platform_post_create_item hooks")
        FunctionPluginManager.instance().hook.idmtools_platform_post_create_item(item=asset_collection, kwargs=kwargs)
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling post_creation")
        asset_collection.post_creation(self.platform)

    def create(self, asset_collection: AssetCollection, do_pre: bool = True, do_post: bool = True, **kwargs) -> Any:
        """
        Creates an AssetCollection from an IDMTools AssetCollection object.

        Also performs pre-creation and post-creation locally and on platform.

        Args:
            asset_collection: AssetCollection to create
            do_pre: Perform Pre creation events for item
            do_post: Perform Post creation events for item
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the id of said item
        """
        if asset_collection.status is not None:
            return asset_collection._platform_object
        if do_pre:
            if logger.isEnabledFor(DEBUG):
                logger.debug("Calling pre_create")
            self.pre_create(asset_collection, **kwargs)
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling platform_create")
        ret = self.platform_create(asset_collection, **kwargs)
        if do_post:
            if logger.isEnabledFor(DEBUG):
                logger.debug("Calling post_create")
            self.post_create(asset_collection, **kwargs)
        return ret

    @abstractmethod
    def platform_create(self, asset_collection: AssetCollection, **kwargs) -> Any:
        """
        Creates an workflow_item from an IDMTools AssetCollection object.

        Args:
            asset_collection: AssetCollection to create
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the id of said item
        """
        pass

    def batch_create(self, asset_collections: List[AssetCollection], display_progress: bool = True, **kwargs) -> \
            List[AssetCollection]:
        """
        Provides a method to batch create asset collections items.

        Args:
            asset_collections: List of asset collection items to create
            display_progress: Show progress bar
            **kwargs:

        Returns:
            List of tuples containing the create object and id of item that was created
        """
        return batch_create_items(asset_collections, create_func=self.create, display_progress=display_progress,
                                  progress_description="Uploading Assets", unit="asset collection", **kwargs)

    @abstractmethod
    def get(self, asset_collection_id: str, **kwargs) -> Any:
        """
        Returns the platform representation of an AssetCollection.

        Args:
            asset_collection_id: Item id of AssetCollection
            **kwargs:

        Returns:
            Platform Representation of an AssetCollection
        """
        pass

    def to_entity(self, asset_collection: Any, **kwargs) -> AssetCollection:
        """
        Converts the platform representation of AssetCollection to idmtools representation.

        Args:
            asset_collection: Platform AssetCollection object

        Returns:
            IDMTools suite object
        """
        return asset_collection
