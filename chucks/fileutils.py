"""
Various tools and toys for helping with file/path operations.
"""

import shutil

def merge_trees(sources, dest):
    """
    Copy all the files from each directory in `sources` into `dest`.

    The last entry in `sources` wins if there are conflicts.

    If `dest` doesn't exists it'll be created; otherwise it's assumed to be empty.
    """

    for source in sources:
        for p in source.walk():
            destpath = dest.child(*source.rel_path_to(p).components())
            if p.isdir() and not destpath.exists():
                destpath.mkdir()
            elif p.isfile():
                shutil.copyfile(p, destpath)

def create_dir(d):
    """
    Create a directory if it doesn't exist.
    """
    if d.exists() and d.listdir():
        raise EnvironmentError("%s exists and is not empty." % d)
    d.mkdir(parents=True)
