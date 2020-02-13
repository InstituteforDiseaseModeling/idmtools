from uuid import UUID
from idmtools.core import ItemType, EntityStatus
from idmtools.core.interfaces.ientity import IEntity
from idmtools.core.platform_factory import Platform
from idmtools.entities.iplatform import IPlatform


class FilterItem:

    @staticmethod
    def filter_item(platform: IPlatform, item: IEntity, max_simulations: int = None, **kwargs):
        """
        Filter simulations from Experiment or Suite
        Args:
            platform:
            item:
            max_simulations:
            kwargs: extra filters

        Returns: list of simulation ids
        """

        def match_tags(sim: IEntity, tags: dict = {}):
            """
            Check if simulation match tags
            Args:
                sim: simulation
                tags: tags

            Returns: bool True/False
            """
            for k, v in tags.items():
                if k not in sim.tags or sim.tags[k] != v:
                    return False

            return True

        if item.item_type not in [ItemType.EXPERIMENT, ItemType.SUITE]:
            raise ValueError("This method only supports Experiment and Suite types!")

        # retrieve item by id and type
        # item = platform.get_item(item.uid, item.item_type, raw=False)

        # get all possible simulations
        potential_sims = platform.flatten_item(item=item)
        print(potential_sims)

        # filter by status
        status = kwargs.get("status", EntityStatus.SUCCEEDED)
        sims_status_filtered = [sim for sim in potential_sims if sim.status == status]

        # filter tags
        tags = kwargs.get("tags", {})
        sims_tags_filtered = [sim for sim in sims_status_filtered if match_tags(sim, tags)]

        # consider max_simulations for return
        sims_final = sims_tags_filtered[0:max_simulations if max_simulations else len(sims_tags_filtered)]

        # only return uid
        return [s.uid for s in sims_final]


    @classmethod
    def filter_item_by_id(cls, platform: IPlatform, item_id: UUID, item_type: ItemType = ItemType.EXPERIMENT,
                          max_simulations: int = None, **kwargs):
        """
        Filter simulations from Experiment or Suite
        Args:
            platform:
            item_id:
            item_type:
            max_simulations:
            kwargs: extra filters

        Returns: list of simulation ids
        """
        if item_type not in [ItemType.EXPERIMENT, ItemType.SUITE]:
            raise ValueError("This method only supports Experiment and Suite types!")

        # retrieve item by id and type
        item = platform.get_item(item_id, item_type, raw=False)

        return cls.filter_item(platform, item, max_simulations, **kwargs)

        # # get all possible simulations
        # potential_sims = platform.flatten_item(item=item)
        # print(potential_sims)
        #
        # # filter by status
        # sims_filtered = [sim.uid for sim in potential_sims if sim.status == expected_status]
        #
        # # consider max_simulations for return
        # return sims_filtered[0:max_simulations if max_simulations else len(sims_filtered)]


def demo_filter_item():
    platform = Platform('COMPS2')

    # Filter from Experiment
    exp_id = '06da767c-f249-ea11-a2be-f0921c167861'  # 2/5 succeed

    # retrieve item by id and type
    exp = platform.get_item(exp_id, ItemType.EXPERIMENT, raw=False)

    # filter simulations
    sims = FilterItem.filter_item(platform, exp, max_simulations=5)

    print(sims)
    return

    # Filer from Suite
    suite_id = '502b6f0c-2920-ea11-a2be-f0921c167861'  # comps2 staging exp id

    # retrieve item by id and type
    suite = platform.get_item(suite_id, ItemType.SUITE, raw=False)

    # filter simulations
    sims = FilterItem.filter_item(platform, suite)

    print(sims)


def demo_filter_item_by_id():
    platform = Platform('COMPS2')

    # Filter from Experiment
    exp_id = '06da767c-f249-ea11-a2be-f0921c167861'  # 2/5 succeed
    sims = FilterItem.filter_item_by_id(platform, exp_id, ItemType.EXPERIMENT, max_simulations=5)

    # Filer from Suite
    suite_id = '502b6f0c-2920-ea11-a2be-f0921c167861'  # comps2 staging exp id
    # sims = FilterItem.filter_item_by_id(platform, suite_id, ItemType.SUITE)

    print(sims)


if __name__ == '__main__':
    demo_filter_item()
    exit()

    demo_filter_item_by_id()
    exit()


