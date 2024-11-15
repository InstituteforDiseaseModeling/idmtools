import os
import shutil
import sys
from pathlib import Path
import shlex


def main():
    cmd = sys.argv[1]

    if cmd.startswith('singularity'):
        # split the command
        cmd = shlex.split(cmd.replace("\\", "/"))
        # get real executable
        exe = cmd[3]
    else:
        parts = shlex.split(cmd.replace("\\", "/"))
        exe = parts[0]

    # Get exe path
    sim_dir = Path(os.getcwd())
    exe_path = sim_dir.joinpath(exe)

    # See if it is a file
    if exe_path.exists():
        exe = exe_path
    elif shutil.which(exe) is not None:
        exe = Path(shutil.which(exe))
    else:
        print(f"Failed to find executable: {exe}")
        exe = None

    try:
        # moke the file executable
        if exe and not os.access(exe, os.X_OK):
            exe.chmod(0o777)
    except:
        print(f"Failed to change file mode for executable: {exe}")


if __name__ == '__main__':
    main()
