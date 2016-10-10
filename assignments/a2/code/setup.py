from util import dump_pickle
from fs.osfs import OSFS


def pick_file_list():
    wl = OSFS('wiki-large')
    large_list = []
    large_set = set()
    for file in wl.walkfiles():
        large_list.append('wiki-large%s' % file)
        large_set.add(file[file.rfind('/') + 1:])
    dump_pickle((large_list, large_set), 'pickled/wiki-large2.pickle')
    wl.close()

    ws = OSFS('wiki-small')
    small_list = []
    small_set = set()
    for file in ws.walkfiles():
        small_list.append('wiki-small%s' % file)
        small_set.add(file[file.rfind('/') + 1:])
    dump_pickle((small_list, small_set), 'pickled/wiki-small2.pickle')
    ws.close()


if __name__ == '__main__':
    pick_file_list()
