"""
Filtering utility.

Copyright 2025, Gates Foundation. All rights reserved.
"""
from uuid import UUID
from idmtools.core import ItemType, EntityStatus
from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities.iplatform import IPlatform
from idmtools.utils.general import parse_value_tags, TagValue


class FilterItem:
    """
    FilterItem provides a utility to filter items on a platform.
    """

    @staticmethod
    def filter_item(platform: IPlatform, item: IEntity, skip_sims=None, max_simulations: int = None, entity_type: bool = False, **kwargs):
        """
        Filter simulations from an Experiment or Suite using tag and status criteria.

        By default, this filters simulations that have a status of `EntityStatus.SUCCEEDED`.
        Additional filtering can be applied by specifying tag values or tag-based conditions.

        This method supports:
            - Skipping specific simulations by ID
            - Filtering based on simulation status (e.g., FAILED, SUCCEEDED)
            - Tag-based filtering (both exact match and conditional/lambda-based)

        Examples:
            >>> filter_item(platform, experiment, status=EntityStatus.FAILED)
            >>> filter_item(platform, experiment, tags={"Run_Number": "2"})
            >>> filter_item(platform, experiment, tags={"Run_Number": lambda v: 2 <= v <= 10})
            >>> filter_item(platform, experiment, tags={"Coverage": 0.8}, max_simulations=10)

        Args:
            platform (IPlatform): The platform instance to query simulations from.
            item (IEntity): An Experiment or Suite to filter simulations from.
            skip_sims (list, optional): A list of simulation IDs (as strings) to exclude from the results.
            max_simulations (int, optional): Maximum number of simulations to return. Returns all if not set.
            entity_type (bool, optional): If True, return simulation entities instead of just their IDs.
            **kwargs:
                - status (EntityStatus): The status to filter by (default is SUCCEEDED).
                - tags (dict): A dictionary of tag key-value pairs to filter by. Values may be:
                    * A fixed value (e.g., {"Run_Number": 2})
                    * A lambda or callable function for conditional logic
                      (e.g., {"Run_Number": lambda v: 2 <= v <= 10})

        Returns:
            list: A list of simulation IDs or simulation entities (if entity_type=True).
        """
        if skip_sims is None:
            skip_sims = []

        def match_tags(sim: IEntity, tags=None):
            """
            Check if simulation match tags.

            Args:
                sim: simulation
                tags: search tags

            Returns: bool True/False
            """
            # If no tags are provided, treat it as an empty filter (match all)
            if tags is None:
                tags = {}
            # Normalize simulation tag values and wrap them with TagValue for safe comparisons
            # (e.g., allows "5" == 5 and supports operators like >, <, == in tag filters)
            sim_tags = {k: TagValue(v) for k, v in parse_value_tags(sim.tags).items()}

            # Iterate over each tag filter condition
            for k, v in tags.items():
                sim_val = sim_tags.get(k)
                # If the simulation does not have the tag, skip it
                if sim_val is None:
                    return False
                # If the filter value is a callable (e.g., lambda), evaluate the condition
                if callable(v):
                    if not v(sim_val):
                        return False
                # Otherwise, do a direct comparison between the simulation tag and expected value
                elif sim_val != v:
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

        if entity_type:
            return sims_final
        else:
            return [s.id for s in sims_final]

    @classmethod
    def filter_item_by_id(cls, platform: IPlatform, item_id: UUID, item_type: ItemType = ItemType.EXPERIMENT,
                          skip_sims=None, max_simulations: int = None, **kwargs):
        """
        Retrieve and filter simulations from an Experiment or Suite by item ID.

        This method looks up the specified item (Experiment or Suite) by ID on the given platform,
        then filters its simulations using the class's `filter_item()` method.

        Args:
            platform (IPlatform): The platform instance used to fetch the item.
            item_id (UUID): The unique identifier of the Experiment or Suite.
            item_type (ItemType, optional): The type of item (Experiment or Suite). Defaults to Experiment.
            skip_sims (List[str], optional): List of simulation IDs to skip during filtering. Defaults to an empty list.
            max_simulations (int, optional): Maximum number of simulations to return. Defaults to None (no limit).
            **kwargs: Additional keyword arguments passed to `filter_item()`.

        Returns:
            List[str]: A list of filtered simulation IDs.

        Raises:
            ValueError: If the provided `item_type` is not Experiment or Suite.
        """
        if skip_sims is None:
            skip_sims = []
        if item_type not in [ItemType.EXPERIMENT, ItemType.SUITE]:
            raise ValueError("This method only supports Experiment and Suite types!")

        # retrieve item by id and type
        item = platform.get_item(item_id, item_type, raw=False)

        # filter simulations
        return cls.filter_item(platform, item, skip_sims, max_simulations, **kwargs)
