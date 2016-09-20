import os
from argparse import ArgumentTypeError, Action


class FullPaths(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))


def is_dir(dirname):
    if not os.path.isdir(dirname):
        msg = "{0} is not a directory".format(dirname)
        raise ArgumentTypeError(msg)
    else:
        return dirname


def is_file(path):
    if not os.path.isfile(path):
        msg = "{0} is not a file".format(path)
        raise ArgumentTypeError(msg)
    else:
        return path
