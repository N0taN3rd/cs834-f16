import csv
from bs4 import BeautifulSoup
from functional import seq
from random import sample, shuffle


def build_lstransformer(func, seq_to='list'):
    if seq_to == 'list':
        return lambda ilist: seq(ilist).group_by(func).to_list()
    else:
        return lambda ilist: seq(ilist).group_by(func).to_dict()


def ltransformer_group_by(func):
    return lambda ilist: seq(ilist).group_by(func).to_list()


def default_ltransformer():
    return lambda ilist: ilist


def default_random_selector():
    return lambda ilist: sample(ilist, 1)[0]


def selected_list_joiner(selected, out):
    out.extend(selected)


def build_selected_joiner(func):
    def joiner(selected, out):
        return func((selected, out))

    return joiner


def default_formatter(item):
    return '%s\n' % item


def int_formatter(i):
    return '%d\n' % i


def build_formatter(format_s):
    return lambda item: format_s % item


class BeautifulSoupFromFile(object):
    def __init__(self, file_p, mode):
        self.file_p = file_p
        self.file_obj = open(file_p, 'r')
        self.mode = mode
        self.soup = None

    def __enter__(self):
        self.soup = BeautifulSoup(self.file_obj.read(), self.mode)
        return self.soup

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file_obj.close()


class RunCommandSaveOut(object):
    def __init__(self, cline, file_p, print_file=False, command_fun=None):
        self.cline = cline
        self.file_p = file_p
        self.file_obj = open(file_p, 'w')
        self.print_file = print_file
        if command_fun is None:
            raise Exception('RunCommandSaveOut the command_fun was None')
        self.command_fun = command_fun

    def __enter__(self):
        spawn_process = self.command_fun(self.cline, self.file_obj)
        return spawn_process

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file_obj.close()
        if self.print_file:
            with FileLinePrinter(self.file_p):
                one = 1


class AutoSaver(object):
    def __init__(self, save_type, file_name, formatter=default_formatter, selector=None):
        self.file_name = file_name
        self.save_type = save_type()
        self.formatter = formatter
        self.selector = selector

    def __enter__(self):
        return self.save_type

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.selector is None:
            outl = self.save_type
        else:
            outl = self.selector(self.save_type)
        with open(self.file_name, 'w') as out:
            for it in outl:
                out.write(self.formatter(it))


class AutoSaveCsv(object):
    def __init__(self, save_type, file_name, field_names):
        self.file_name = file_name
        self.save_type = save_type()
        self.field_names = field_names

    def __enter__(self):
        return self.save_type

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(self.file_name, 'w') as out:
            writer = csv.DictWriter(out, fieldnames=self.field_names)
            writer.writeheader()
            for it in self.save_type:
                writer.writerow(it)


class SelectFromFile(object):
    def __init__(self, q_file, selector, transformer=default_ltransformer()):
        self.q_file = open(q_file, 'r')
        self.line_transformer = transformer
        self.selector = selector

    def __enter__(self):
        lines = self.line_transformer(self.q_file.readlines())
        return self.selector(lines)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.q_file.close()


class RandFinderFile(object):
    def __init__(self, q_file, transformer=default_ltransformer(), selector=default_random_selector()):
        self.q_file = open(q_file, 'r')
        self.line_transformer = transformer
        self.random_selector = selector

    def __enter__(self):
        lines = self.line_transformer(self.q_file.readlines())
        return self.random_selector(lines)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.q_file.close()


class RandFinderSaver(RandFinderFile):
    def __init__(self, q_file, save_p, save_type, out_adder, formatter=default_formatter, sselector=None,
                 transformer=default_ltransformer(), selector=default_random_selector()):
        super(RandFinderSaver, self).__init__(q_file=q_file, transformer=transformer, selector=selector)
        self.selected = None
        self.save_p = save_p
        self.save_type = save_type
        self.formatter = formatter
        self.sselector = sselector
        self.out_adder = out_adder

    def __enter__(self):
        self.selected = super(RandFinderSaver, self).__enter__()
        return self.selected

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(RandFinderSaver, self).__exit__(exc_tb, exc_val, exc_tb)
        with AutoSaver(self.save_type, self.save_p, formatter=self.formatter, selector=self.sselector) as out:
            self.out_adder(self.selected, out)


class FileLinePrinter(object):
    def __init__(self, file_p, line_transformer=lambda line: line.rstrip().lstrip()):
        self.file_p = open(file_p, 'r')
        self.line_transformer = line_transformer

    def __enter__(self):
        for line in map(self.line_transformer, self.file_p):
            print(line)
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file_p.close()


class CleanFileLines(object):
    def __init__(self, file_p, remove_fun, save_back=False, sort_output=lambda x: x):
        self.file_p = file_p
        self.file_obj = open(file_p, 'r')
        self.remove_fun = remove_fun
        self.clean_lines = []
        self.save_back = save_back
        self.sort_output = sort_output

    def __enter__(self):
        for line in self.sort_output(self.file_obj):
            self.clean_lines.append(self.remove_fun(line))
        return self.clean_lines

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file_obj.close()
        if self.save_back:
            with AutoSaver(list, self.file_p) as out:
                out.extend(self.clean_lines)