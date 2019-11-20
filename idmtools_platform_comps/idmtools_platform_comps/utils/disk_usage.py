import concurrent.futures
import functools
import json
from logging import getLogger
import humanfriendly
import pandas as pd
import os
import sys
from COMPS.Data import QueryCriteria, Experiment
from diskcache import FanoutCache
from tqdm import tqdm
from idmtools_platform_comps.comps_platform import COMPSPlatform
from idmtools_platform_comps.utils.lookups import get_all_experiments_for_user

logger = getLogger(__name__)


class ExperimentInfo:
    def __init__(self, id, name, owner, size, sims):
        self.id = id
        self.name = name
        self.owner = owner
        self.size = size
        self.sims = sims
        self.size_str = humanfriendly.format_size(size)


class DiskSpaceUsage:
    # How many experiments to display in the TOP?
    TOP_COUNT = 15  # default

    # Usernames
    OWNERS = []  # default: will  be the login user passed in

    @staticmethod
    def get_experiment_info(experiment: Experiment, cache, refresh):
        """
        Adds the experiment information for a given experiment to the cache:
        - raw_size: the size in bytes
        - size: the formatted size (in KB, MB or GB)
        - sims: the number of simulations
        This function is used by the process pool to parallelize the retrieval of experiment info
        Args:
            experiment: The experiment to analyze
            cache:
            refresh:

        Returns:

        """
        if experiment.id in cache and cache.get(experiment.id) and not refresh:
            return

        # Try to get the simulations
        try:
            simulations = experiment.get_simulations(
                query_criteria=QueryCriteria().select(['id']).select_children(['hpc_jobs']))
        except KeyError:
            # No simulations found or error -> set None
            cache.set(experiment.id, None)
            return

        # Calculate the size
        size = sum(s.hpc_jobs[0].output_directory_size for s in simulations if s.hpc_jobs)

        # Set the info for this particular experiment in the cache
        cache.set(experiment.id,
                  ExperimentInfo(experiment.id, experiment.name, experiment.owner, size, len(simulations)))

    @staticmethod
    def exp_str(info, display_owner=True):
        """
        Format an experiment and its information to a string.
        """
        string = "{} ({})".format(info.name, info.id)
        if display_owner:
            string += " - {}".format(info.owner)

        string += " : {} in {} simulations".format(info.size_str, info.sims)
        return string

    @staticmethod
    def top_count_experiments(experiments_info):
        """
        Displays the top count of all experiments analyzed
        """
        print("Top {} Experiments".format(DiskSpaceUsage.TOP_COUNT))
        for order, info in enumerate(
                sorted(experiments_info, key=lambda i: i.size, reverse=True)[:DiskSpaceUsage.TOP_COUNT]):
            print("{}. {}".format(order + 1, DiskSpaceUsage.exp_str(info)))

    @staticmethod
    def total_size_per_user(experiments_info):
        """
        Displays the total disk space occupied per user
        """
        print("Size per user")
        size_per_users = {
            o: sum(i.size for i in experiments_info if i.owner == o)
            for o in DiskSpaceUsage.OWNERS
        }

        for order, owner in enumerate(sorted(size_per_users, key=size_per_users.get, reverse=True)):
            print(
                "{}. {} with a total of {}".format(order + 1, owner, humanfriendly.format_size(size_per_users[owner])))

    @staticmethod
    def top_count_experiments_per_user(experiments_info):
        """
        Display the top count biggest experiments per user
        """
        experiments_per_owner = {}

        for info in experiments_info:
            if info.owner not in experiments_per_owner:
                experiments_per_owner[info.owner] = {}

            experiments_per_owner[info.owner][info.id] = info

        for owner, experiments in experiments_per_owner.items():
            print("Top {} experiments for {}".format(DiskSpaceUsage.TOP_COUNT, owner))
            for order, eid in enumerate(
                    sorted(experiments, key=lambda e: experiments[e].size, reverse=True)[:DiskSpaceUsage.TOP_COUNT]):
                print("{}. {}".format(order + 1, DiskSpaceUsage.exp_str(experiments[eid], False)))
            print("")

    @staticmethod
    def gather_experiment_info(refresh=False, max_workers: int = 6):
        # Create/open the cache
        current_folder = os.path.dirname(os.path.realpath(__file__))
        cache_folder = os.path.join(current_folder, "cache")
        cache = FanoutCache(shards=6, directory=cache_folder)

        # All experiments
        all_experiments = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            for result in tqdm(executor.map(get_all_experiments_for_user, DiskSpaceUsage.OWNERS),
                               total=len(DiskSpaceUsage.OWNERS)):
                all_experiments.extend(result)

            all_experiments_len = len(all_experiments)

            print("Analyzing disk space for:")
            print(" | {} experiments".format(all_experiments_len))
            print(" | Users: {}".format(", ".join(DiskSpaceUsage.OWNERS)))

            exp_opts = functools.partial(DiskSpaceUsage.get_experiment_info, cache=cache, refresh=refresh)
            for result in tqdm(executor.map(exp_opts, all_experiments),
                               total=all_experiments_len,
                               desc="Gathering Experiment info"):
                pass

        sys.stdout.write("\r | Experiment analyzed: {}/{}".format(all_experiments_len, all_experiments_len))
        sys.stdout.flush()
        print("\n")

        # Get all the results
        experiments_info = [cache.get(e.id) for e in all_experiments if cache.get(e.id)]
        cache.close()

        return experiments_info

    @staticmethod
    def display(platform: COMPSPlatform, users, top=15, save=False, refresh=False):
        DiskSpaceUsage.OWNERS = users
        DiskSpaceUsage.TOP_COUNT = top if top else 15

        # Get all the results
        experiments_info = DiskSpaceUsage.gather_experiment_info(refresh)

        # Display
        print("\n---------------------------")
        DiskSpaceUsage.top_count_experiments(experiments_info)
        print("\n---------------------------")
        DiskSpaceUsage.total_size_per_user(experiments_info)
        print("\n---------------------------")
        DiskSpaceUsage.top_count_experiments_per_user(experiments_info)

        # save to a csv file
        if save:
            DiskSpaceUsage.save_to_file(experiments_info)

    @staticmethod
    def save_to_file(experiments_info):
        # collect columns
        variables = experiments_info[0].__dict__.keys()

        # load data as a DataFrame
        df = pd.DataFrame([[getattr(i, j) for j in variables] for i in experiments_info], columns=variables)

        # save to a csv file
        df.to_csv('diskspace.csv')


class DiskEncoder(json.JSONEncoder):

    def default(self, o):
        # First get the dict
        d = o.__dict__

        return d
