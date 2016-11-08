import pickle
from fs.osfs import OSFS
from shutil import copyfile

wsmall = 'pickled/wiki-small.pickle'


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
    dump_pickle((small_list, small_set), 'pickled/wiki-small.pickle')
    ws.close()


if __name__ == '__main__':
    ws = OSFS('wiki-small')
    small_list = []
    for file in ws.walkfiles():
        print(file)
        copyfile('wiki-small%s' % file,'htmls/%s'%file[file.rfind('/') + 1:])
    ws.close()

