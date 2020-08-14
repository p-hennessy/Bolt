import os
import importlib


class attrdict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def snakecase_to_camelcase(string):
    return ''.join(x.title() for x in string.split('_'))


def find_plugins(path):
    for file in os.listdir(path):
        if not file.startswith('__'):
            if file.endswith(".py"):
                fullname = os.path.splitext(os.path.basename(file))[0]

                try:
                    module = importlib.machinery.SourceFileLoader(fullname, os.path.join(path, file)).load_module()
                except ImportError:
                    continue

                yield module


def readable_time(elapsed):
    readable = ""

    days = int(elapsed / (60 * 60 * 24))
    hours = int((elapsed / (60 * 60)) % 24)
    minutes = int((elapsed % (60 * 60)) / 60)
    seconds = int(elapsed % 60)

    if(days > 0):
        readable += str(days) + " days "

    if(hours > 0):
        readable += str(hours) + " hours "

    if(minutes > 0):
        readable += str(minutes) + " minutes "

    if(seconds > 0):
        readable += str(seconds) + " seconds "

    return readable
