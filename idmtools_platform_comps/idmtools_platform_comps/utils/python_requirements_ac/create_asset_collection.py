import os
import re
import sys
from hashlib import md5

from COMPS import Client
from COMPS.Data import AssetCollectionFile, QueryCriteria
from COMPS.Data import Experiment
from COMPS.Data.AssetCollection import AssetCollection

MD5_KEY = 'idmtools-requirements-md5'
AC_FILE = 'ac_info.txt'
LIBRARY_ROOT_PREFIX = 'L'


def unc_path_to_docker_path(p):
    mapping = os.environ['COMPS_DATA_MAPPING'].split(';')
    return re.sub(mapping[1].replace('\\', '\\\\'), mapping[0], p, flags=re.IGNORECASE).replace('\\', '/')


def calculate_md5(file_path) -> str:
    """
    Calculate and md5
    """
    with open(file_path, 'rb') as f:
        md5calc = md5()
        md5calc.update(f.read())
        md5_checksum_str = md5calc.hexdigest()
    return md5_checksum_str


def build_asset_file_list(comps_sim, prefix=LIBRARY_ROOT_PREFIX):
    """
    Utility function to build all library files
    Args:
        comps_sim: given simulation
        prefix: used to identify library files

    Returns: file paths as a list
    """
    metadata = comps_sim.retrieve_output_file_info([])
    output_folder = []
    for m in metadata:
        parts = m.path_from_root.split('/')
        if parts[0] == prefix:
            d = {'friendly_name': m.friendly_name, 'path_from_root': m.path_from_root, 'url': m.url}
            output_folder.append(d)

    return output_folder


def get_first_simulation_of_experiment(exp_id):
    """
    Retrieve the first simulation from an experiment
    Args:
        exp_id: use input (experiment id)

    Returns: list of files paths
    """
    comps_exp = Experiment.get(exp_id)
    comps_sims = comps_exp.get_simulations(QueryCriteria().select_children('hpc_jobs'))
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
    asset_files = build_asset_file_list(comps_sim, prefix=LIBRARY_ROOT_PREFIX)
    print('asset files count: ', len(asset_files))

    # Output files
    max_files = 10
    print('Display the fist 10 files:\n', asset_files[0:max_files])

    ac = AssetCollection()
    tags = {MD5_KEY: md5_str}
    ac.set_tags(tags)
    experiment_path = unc_path_to_docker_path(comps_sim.hpc_jobs[-1].working_directory)

    # Create asset collection
    path_to_ac = 'L'
    file_mapping = dict()
    for af in asset_files:
        dirpath = af['path_from_root']
        frp = os.path.relpath(dirpath, path_to_ac) if dirpath != path_to_ac else ''
        true_path = os.path.join(experiment_path, LIBRARY_ROOT_PREFIX, frp, af['friendly_name'])
        rp = os.path.join('site_packages', frp)  # add all library under site_packages
        file_mapping[os.path.join(rp, af['friendly_name'])] = true_path
        ac.add_asset(AssetCollectionFile(af['friendly_name'], rp, md5_checksum=calculate_md5(true_path)))

    missing_files = ac.save(return_missing_files=True)

    # If COMPS responds that we're missing some files, then try creating it again,
    # uploading only the files that COMPS doesn't already have.
    if missing_files:
        print(f"Uploading files not in comps: [{','.join([str(u) for u in missing_files])}]")

        ac2 = AssetCollection()
        ac2.set_tags(tags)

        for acf in ac.assets:
            if acf.md5_checksum in missing_files:
                rp = acf.relative_path
                fn = acf.file_name
                acf2 = AssetCollectionFile(fn, rp, tags=acf.tags)
                ac2.add_asset(acf2, file_mapping[os.path.join(rp, fn)])
            else:
                ac2.add_asset(acf)

        ac2.save()
        ac = ac2
    # Output ac
    print('ac_id: ', ac.id)

    # write ac_id to file ac_info.txt
    with open(AC_FILE, 'w') as outfile:
        outfile.write(str(ac.id))


if __name__ == "__main__":
    main()
