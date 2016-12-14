import pickle
from fs.osfs import OSFS

wsmall = 'pickled/wsmall.pickle'
wsmalln = 'pickled/wsmall_new.pickle'


def dump_pickle(obj, file):
    with open(file, 'wb') as out:
        pickle.dump(obj, out)


def read_pickle(name):
    with open(name, "rb") as input_file:
        return pickle.load(input_file)


def pick_file_list():
    ws = OSFS('wiki-small')
    small_list = []
    small_set = set()
    for file in ws.walkfiles():
        small_list.append('wiki-small%s' % file)
        small_set.add(file[file.rfind('/') + 1:])
    dump_pickle((small_list, small_set), 'pickled/wsmall.pickle')
    ws.close()


if __name__ == '__main__':
    pick_file_list()
