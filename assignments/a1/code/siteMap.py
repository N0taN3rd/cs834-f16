from urllib.parse import quote_plus as quote
from argparse import ArgumentParser
from arrow import Arrow
from fs.osfs import OSFS
from yattag import Doc, indent
from shared_code import FullPaths, is_dir

dots = False


def accept(name, moreDots=dots):
    if moreDots:
        return True
    else:
        return not name.startswith('.')


if __name__ == '__main__':
    parser = ArgumentParser(description="Create a sitemap of a directory on your local file system", prog='sitemap',
                            usage='%(prog)s [options]')
    parser.add_argument('-dir', '--directory', help='directory to use', action=FullPaths, type=is_dir)
    parser.add_argument('-dots', help='include dot files', action='store_true')
    args = parser.parse_args()
    dir = OSFS(args.directory)
    dots = args.dots
    dirs = []
    skipFirst = True
    doc, tag, text = Doc().tagtext()
    with tag('urlSet', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"):
        for name, stats in dir.listdirinfo(files_only=True):
            if accept(name):
                with tag('url'):
                    with tag('loc'):
                        text('http://www.example.com/%s' % quote(name))
                    with tag('lastmod'):
                        text(str(Arrow.utcfromtimestamp(stats['modified_time'].timestamp())))
        for aDir in dir.walkdirs():
            if skipFirst:
                skipFirst = False
                continue
            if accept(aDir[1:None]):
                for name, stats in dir.listdirinfo(path=aDir, files_only=True):
                    if accept(name):
                        with tag('url'):
                            with tag('loc'):
                                text('http://www.example.com%s/%s' %(aDir,quote(name)))
                            with tag('lastmod'):
                                text(str(Arrow.utcfromtimestamp(stats['modified_time'].timestamp())))


    dir.close()
    result = indent(
        doc.getvalue(),
        indentation=' ' * 2,
        newline='\r\n'
    )

    print(result)
