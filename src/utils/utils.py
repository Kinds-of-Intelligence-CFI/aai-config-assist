import errno
import os


def try_mkdir(path: str) -> None:
    try:
        os.mkdir(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def create_directory_if_not_exists(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"Directory '{directory}' did not exist and was created.")
