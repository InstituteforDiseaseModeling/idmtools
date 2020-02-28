import os
import sys
from COMPS.Data.AssetCollection import AssetCollection
from COMPS.Data import AssetCollectionFile
from COMPS.Data import Experiment
from COMPS import Client

MD5_KEY = 'idmtools-requirements-md5'
AC_FILE = 'ac_info.txt'


def build_asset_file_list(comps_sim, prefix='Libraries/'):
    """
    Utility function to build all library files
    Args:
        comps_sim: given simulation
        prefix: used to identify library files

    Returns: file paths as a list
    """
    metadata = comps_sim.retrieve_output_file_info([])
    output_folder = [{'friendly_name': m.friendly_name, 'path_from_root': m.path_from_root, 'url': m.url} for m in
                     metadata if m.path_from_root.startswith(prefix)]
    return output_folder


def get_first_simulation_of_experiment(exp_id):
    """
    Retrieve the first simulation from an experiment
    Args:
        exp_id: use input (experiment id)

    Returns: list of files paths
    """
    comps_exp = Experiment.get(exp_id)
    comps_sims = comps_exp.get_simulations()
    comps_sim = comps_sims[0]

    return comps_sim


def get_data(url):
    """
    Get content of a file
    Args:
        url: file location
    Returns: file content as byte string
    """
    i = url.find('/asset/')
    if i == -1:
        raise RuntimeError('Unable to parse asset url: ' + url)

    resp = Client.get(url[i:])
    byte_str = resp.content
    return byte_str


def main():
    print(sys.argv)

    if len(sys.argv) < 3:
        raise Exception(
            "The script needs to be called with `python <model.py> <experiment_id> <md5_str> <endpoint>'.\n{}".format(
                " ".join(sys.argv)))

    # Get the experiments
    exp_id = sys.argv[1]
    print('exp_id: ', exp_id)

    # Get mds
    md5_str = sys.argv[2]
    print('md5_str: ', md5_str)

    # Get endpoint
    endpoint = sys.argv[3]
    print('endpoint: ', endpoint)

    client = Client()
    client.login(endpoint)

    # Retrieve the first simulation of the experiment
    comps_sim = get_first_simulation_of_experiment(exp_id)
    print('sim_id: ', comps_sim.id)

    # Build files metadata
    asset_files = build_asset_file_list(comps_sim, prefix='Libraries/')
    print('asset files count: ', len(asset_files))

    # Output files
    max_files = 10
    print('Display the fist 10 files:\n', asset_files[0:max_files])

    ac = AssetCollection()
    tags = {MD5_KEY: md5_str}
    ac.set_tags(tags)

    # Create asset collection
    path_to_ac = 'Libraries'
    for af in asset_files:
        dirpath = af['path_from_root']
        rp = os.path.relpath(dirpath, path_to_ac) if dirpath != path_to_ac else ''
        ac.add_asset(AssetCollectionFile(af['friendly_name'], rp), data=get_data(af['url']))

    ac.save()

    # Output ac
    print('ac_id: ', ac.id)

    # write ac_id to file ac_info.txt
    with open(AC_FILE, 'w') as outfile:
        outfile.write(str(ac.id))


if __name__ == "__main__":
    main()
