import os


def get_paths(path_in_project):
    return os.path.join(os.path.dirname(__file__), path_in_project)