import glob
from concurrent.futures._base import as_completed

from concurrent.futures.thread import ThreadPoolExecutor

import uuid

import hashlib

from io import BytesIO
from tqdm import tqdm
from typing import Union, BinaryIO
import os
import argparse
from COMPS import Client
from COMPS.Data import Experiment, QueryCriteria, AssetCollection, AssetCollectionFile
from COMPS.Data import WorkItem
from COMPS.Data import AssetFile

from idmtools.entities.simulation import Simulation


def calculate_md5(filename: str, chunk_size: int = 8192) -> str:
    """
    Calculate MD5

    Args:
        filename: Filename to caclulate md5 for
        chunk_size: Chunk size

    Returns:

    """
    with open(filename, "rb") as f:
        return calculate_md5_stream(f, chunk_size)


def calculate_md5_stream(stream: Union[BytesIO, BinaryIO], chunk_size: int = 8192, ):
    """
    Calculate md5 on stream
    Args:
        chunk_size:
        stream:

    Returns:
        md5 of stream
    """
    file_hash = hashlib.md5()
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        file_hash.update(chunk)
    return file_hash.hexdigest()


def gather_files(directory, file_patterns, assets, prefix=None):
    files = set()
    for pattern in file_patterns:
        for file in glob.glob(os.path.join(directory, pattern), recursive=True):
            if os.path.isfile(file):
                short_name = file.replace(directory + os.path.sep, "")
                dest_name = os.path.join(prefix if prefix else '', short_name)
                if short_name.startswith("Assets"):
                    if assets:
                        files.add((file, dest_name, uuid.UUID(calculate_md5(file))))
                else:
                    if file not in files:
                        files.add((file, dest_name, uuid.UUID(calculate_md5(file))))

    return files


def gather_files_from_related(wi):
    files = set()
    futures = []
    pool = ThreadPoolExecutor()
    for experiment in wi.get_related_experiments():
        experiment: Experiment
        # TODO grab asset if specified
        for sim in experiment.get_simulations(QueryCriteria().select_children('hpc_jobs')):
            futures.append(pool.submit(gather_files, sim.hpc_jobs[0].working_directory, args.file_pattern, False, str(sim.id)))

    for simulation in wi.get_related_simulations():
        futures.append(pool.submit(gather_files, simulation.hpc_jobs[0].working_directory, args.file_pattern, args.assets))

    for workitem in wi.get_related_work_items():
        wi: WorkItem
        if args.assets:
            # get workitems assets
            pass
        futures.append(pool.submit(gather_files, wi.working_directory, args.file_pattern, False))

    for future in tqdm(as_completed(futures), total=len(futures), desc="Filtering relations for files"):
        files.update(future.result())
    return files


def create_asset_collection(files):
    ac = AssetCollection()
    ac_map = dict()
    for file in files:
        fn = os.path.basename(file[1])
        acf = AssetCollectionFile(file_name=fn, relative_path=file[1].replace(fn, "").strip("/"), md5_checksum=file[2])
        ac_map[file[2]] = (acf, file[0])
        ac.add_asset(acf)

    # do initial save to see what assets are in comps
    missing_files = ac.save(return_missing_files=True)
    if missing_files:
        print(f"{len(missing_files)} not currently in COMPS as Assets")

        ac2 = AssetCollection()
        new_files = 0
        for cksum, adetails in ac_map.items():
            if cksum in missing_files:
                new_files += 1
                acf = AssetCollectionFile(file_name=adetails[0].file_name, relative_path=adetails[0].relative_path)
                ac2.add_asset(acf, adetails[1])
            else:
                ac2.add_asset(adetails[0])
        print(f"Saving {new_files} assets to comps")
        ac2.save()
        ac = ac2
    return ac


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Assetize Output script")
    parser.add_argument("--file-pattern", action='append', help="File Pattern to Assetize")
    # TODO Exlcudes
    # TODO tags
    #parser.add_argument("--exclude-pattern", action='append', help="File Pattern to Assetize")
    parser.add_argument("--assets", default=False, action='store_true', help="Include Assets")

    args = parser.parse_args()

    # load the workitem
    client = Client()
    client.login(os.environ['COMPS_SERVER'])
    wi = WorkItem.get(os.environ['COMPS_WORKITEM_GUID'])
    files = gather_files_from_related(wi)
    ac = create_asset_collection(files)
    print(ac.id)
