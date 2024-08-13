import argparse
import sys
from pathlib import Path

parent = Path(__file__).resolve().parent
sys.path.append(str(parent))
from utils import delete_containers_by_image_prefix

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_prefix", default="docker-production-public.packages.idmod.org/idmtools/container-rocky-runtime", type=str)
    args = parser.parse_args()
    delete_containers_by_image_prefix(args.image_prefix)