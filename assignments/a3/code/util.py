import pickle
from fs.osfs import OSFS
from shutil import copyfile


def dump_pickle(obj, file):
    with open(file, 'wb') as out:
        pickle.dump(obj, out)


def read_pickle(name):
    with open(name, "rb") as input_file:
        return pickle.load(input_file)


def copy_wiki():
    ws = OSFS('wiki-small')
    for file in ws.walkfiles():
        print(file)
        copyfile('wiki-small%s' % file, 'htmls/%s' % file[file.rfind('/') + 1:])
    ws.close()


if __name__ == '__main__':
    copy_wiki()
