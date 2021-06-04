"""
Filtering utility.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from uuid import UUID
from idmtools.core import ItemType, EntityStatus
from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities.iplatform import IPlatform


class FilterItem:
    """
    FilterItem provides a utility to filter items on a platform.
    """

    @staticmethod
    def filter_item(platform: IPlatform, item: IEntity, skip_sims=None, max_simulations: int = None, **kwargs):
        """
        Filter simulations from Experiment or Suite, by default it filter status with Succeeded.

        If user wants to filter by other status, it also can be done, for example:

        .. code-block:: python

                filter_item(platform, exp, status=EntityStatus.FAILED

        If user wants to filter by tags, it also can be done, for example:

        .. code-block:: python

                filter_item(platform, exp, tags={'Run_Number': '2'})

        Args:
            platform: Platform item
            item: Item to filter
            skip_sims: list of sim ids
            max_simulations: Total simulations
            kwargs: extra filters

        Returns: list of simulation ids
        """
        if skip_sims is None:
            skip_sims = []

        def match_tags(sim: IEntity, tags=None):
            """
            Check if simulation match tags.

            Args:
                sim: simulation
                tags: tags

            Returns: bool True/False
            """
            if tags is None:
                tags = {}
            for k, v in tags.items():
                if k not in sim.tags or sim.tags[k] != v:
                    return False

            return True

        if item.item_type not in [ItemType.EXPERIMENT, ItemType.SUITE]:
            raise ValueError("This method only supports Experiment and Suite types!")

        # get all possible simulations
        potential_sims = platform.flatten_item(item=item)

        # filter by status
        status = kwargs.get("status", EntityStatus.SUCCEEDED)
        sims_status_filtered = [sim for sim in potential_sims if sim.status == status]

        # filter tags
        tags = kwargs.get("tags", {})
        sims_tags_filtered = [sim for sim in sims_status_filtered if match_tags(sim, tags)]

        # filter sims
        sims_id_filtered = [sim for sim in sims_tags_filtered if str(sim.uid) not in skip_sims]

        # consider max_simulations for return
        sims_final = sims_id_filtered[0:max_simulations if max_simulations else len(sims_id_filtered)]

        # only return uid
        return [s.uid for s in sims_final]

    @classmethod
    def filter_item_by_id(cls, platform: IPlatform, item_id: UUID, item_type: ItemType = ItemType.EXPERIMENT, skip_sims=None, max_simulations: int = None, **kwargs):
        """
        Filter simulations from Experiment or Suite.

        Args:
            platform: COMPSPlatform
            item_id: Experiment/Suite id
            item_type:  Experiment or Suite
            skip_sims: list of sim ids
            max_simulations: #sims to be returned
            kwargs: extra filters

        Returns: list of simulation ids
        """
        if skip_sims is None:
            skip_sims = []
        if item_type not in [ItemType.EXPERIMENT, ItemType.SUITE]:
            raise ValueError("This method only supports Experiment and Suite types!")

        # retrieve item by id and type
        item = platform.get_item(item_id, item_type, raw=False)

        # filter simulations
        return cls.filter_item(platform, item, skip_sims, max_simulations, **kwargs)
