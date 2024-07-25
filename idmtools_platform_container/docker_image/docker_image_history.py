"""This script fetches the history of a Docker image and prints it in a tabular format."""
import argparse
import re
import shutil
import subprocess
import pandas as pd
from tabulate import tabulate


def parse_size(size_str):
    """
    Parse the size string from Docker and convert to bytes.
    Args:
        size_str:

    Returns:
        Size in bytes
    """
    """Parse the size string from Docker and convert to bytes."""
    units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
    size_str = size_str.upper().replace(" ", "")
    num, unit = re.findall(r'([0-9.]+)([A-Z]+)', size_str)[0]
    return float(num) * units.get(unit, 1)


def format_size(size_in_bytes):
    """
    Convert a size in bytes to a human-readable string of the most appropriate unit.
    Args:
        size_in_bytes:

    Returns:
        Size in human-readable format
    """
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"  # Bytes
    elif size_in_bytes < 1024**2:
        return f"{size_in_bytes / 1024:.2f} KB"  # Kilobytes
    elif size_in_bytes < 1024**3:
        return f"{size_in_bytes / 1024**2:.2f} MB"  # Megabytes
    elif size_in_bytes < 1024**4:
        return f"{size_in_bytes / 1024**3:.2f} GB"  # Gigabytes
    else:
        return f"{size_in_bytes / 1024**4:.2f} TB"  # Terabytes


def get_docker_image_history(image_id_or_name):
    """
    Fetch the history of a Docker image.
    Args:
        image_id_or_name:

    Returns:
        df
    """
    result = subprocess.run(
        ['docker', 'history', '--no-trunc', image_id_or_name, '--format', '{{.ID}}|{{.CreatedBy}}|{{.Size}}'],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    if result.returncode != 0:
        print("Error fetching Docker image history")
        return None

    history_lines = result.stdout.strip().split('\n')
    data = [line.split('|') for line in history_lines]
    for i, line in enumerate(data):
        if len(line) == 4:
            data[i] = [line[0], line[1] + " " + line[2], line[3]]
    df = pd.DataFrame(data, columns=['LAYER ID', 'COMMAND', 'SIZE'])
    df = df.iloc[:, -2:]
    return df


def main(image_id):
    """
    This script fetches the history of a Docker image and prints it in a tabular format.
    Returns:
        None
    """
    df = get_docker_image_history(image_id)
    total_size = sum(parse_size(size) for size in df['SIZE'])
    size = format_size(total_size)
    if df is not None:
        terminal_width = shutil.get_terminal_size().columns
        max_command_width = terminal_width - 10
        table = tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False,
                         maxcolwidths=[None, max_command_width, None])
        print(table)
        with open('rocky_meta_runtime.txt', 'w', encoding='utf-8') as outputfile:
            outputfile.write(f"Total size: {size}\n\n")
            outputfile.write(table)


if __name__ == "__main__":
    if __name__ == "__main__":
        parser = argparse.ArgumentParser("Get Image Build History")
        parser.add_argument("--image_id", default="10bed3221522", help="Docker image id")
        args = parser.parse_args()
        main(args.image_id)
