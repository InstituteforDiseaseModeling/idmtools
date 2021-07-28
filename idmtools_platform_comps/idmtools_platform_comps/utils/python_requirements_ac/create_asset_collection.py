"""idmtools create asset collection script.

This is part of the RequirementsToAssetCollection tool. This is ran on the SSMT to convert installed files to a AssetCollection.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import sys
from COMPS import Client
from COMPS.Data import AssetCollectionFile, QueryCriteria
from COMPS.Data import Experiment
from COMPS.Data.AssetCollection import AssetCollection
from idmtools.utils.hashing import calculate_md5

MD5_KEY = 'idmtools-requirements-md5-{}'
AC_FILE = 'ac_info.txt'
LIBRARY_ROOT_PREFIX = 'L'


def build_asset_file_list(prefix=LIBRARY_ROOT_PREFIX):
    """
    Utility function to build all library files.

    Args:
        prefix: used to identify library files

    Returns: file paths as a list
    """
    output = []
    for root, _, filenames in os.walk(prefix):
        for filename in filenames:
            asset = AssetCollectionFile(file_name=os.path.basename(filename),
                                        relative_path=os.path.join("site-packages",
                                                                   root.replace(prefix, "").strip("/")).strip("/"),
                                        md5_checksum=calculate_md5(os.path.join(root, filename))
                                        )
            output.append(asset)

    return output


def get_first_simulation_of_experiment(exp_id):
    """
    Retrieve the first simulation from an experiment.

    Args:
        exp_id: use input (experiment id)

    Returns: list of files paths
    """
    comps_exp = Experiment.get(exp_id)
    comps_sims = comps_exp.get_simulations(QueryCriteria().select_children('hpc_jobs'))
    comps_sim = comps_sims[0]

    return comps_sim


def main():  # pragma: no cover
    """Main entry point for our create asset collection script."""
    print(sys.argv)

    if len(sys.argv) < 3:
        raise Exception(
            "The script needs to be called with `python <model.py> <experiment_id> <endpoint> <os_str>'.\n{}".format(
                " ".join(sys.argv)))

    # Get the experiments
    exp_id = sys.argv[1]
    print('exp_id: ', exp_id)

    # Get endpoint
    endpoint = sys.argv[2]
    print('endpoint: ', endpoint)

    # Platform key
    os_target = sys.argv[3]
    print('os: ', os_target)

    client = Client()
    client.login(endpoint)

    # Retrieve the first simulation of the experiment
    comps_sim = get_first_simulation_of_experiment(exp_id)
    print('sim_id: ', comps_sim.id)

    # Build files metadata
    base_path = os.path.join(comps_sim.hpc_jobs[-1].working_directory, LIBRARY_ROOT_PREFIX)
    asset_files = build_asset_file_list(prefix=base_path)
    print('asset files count: ', len(asset_files))

    # Output files
    max_files = 10
    print('Display the first 10 files:\n',
          "\n".join([f"{a.relative_path}/{a.file_name}" for a in asset_files[0:max_files]]))

    # Retrieve experiment's tags
    comps_exp = Experiment.get(exp_id, QueryCriteria().select_children('tags'))
    exp_tags = comps_exp.tags

    # Retrieve experiment's tags
    _reserved_tag = ['idmtools', 'task_type', MD5_KEY.format(os_target)]
    comps_exp = Experiment.get(exp_id, QueryCriteria().select_children('tags'))
    user_tags = {key: value for key, value in comps_exp.tags.items() if key not in _reserved_tag}

    # Get md5_str
    md5_str = exp_tags.get(MD5_KEY.format(os_target), None)

    # Collect ac's tags
    ac = AssetCollection()
    tags = {MD5_KEY.format(os_target): md5_str}
    tags.update(user_tags)
    ac.set_tags(tags)

    # Create asset collection
    for af in asset_files:
        ac.add_asset(af)

    sys.stdout.flush()
    missing_files = ac.save(return_missing_files=True)

    # If COMPS responds that we're missing some files, then try creating it again,
    # uploading only the files that COMPS doesn't already have.
    if missing_files:
        print(f"Total of {len(ac.assets) - len(missing_files)} files currently in comps. Resolving missing files")
        ac2 = AssetCollection()
        ac2.set_tags(tags)

        for acf in ac.assets:
            if acf.md5_checksum in missing_files:
                rp = acf.relative_path
                fn = acf.file_name
                acf2 = AssetCollectionFile(fn, rp, tags=acf.tags)
                rfp = os.path.join(base_path, rp.replace("site-packages", "").strip(os.path.sep), fn)
                ac2.add_asset(acf2, rfp)
            else:
                ac2.add_asset(acf)

        print("\n\n\n=====================\nUploading files not in comps: " + "\n".join(
            [f"{a.relative_path}/{a.file_name}" for a in ac2.assets if
             a.md5_checksum in missing_files or a.md5_checksum is None]))

        sys.stdout.flush()
        ac2.save()
        ac = ac2
    # Output ac
    print('ac_id: ', ac.id)

    # write ac_id to file ac_info.txt
    with open(AC_FILE, 'w') as outfile:
        outfile.write(str(ac.id))
    sys.stdout.flush()


if __name__ == "__main__":  # pragma: no cover
    main()
