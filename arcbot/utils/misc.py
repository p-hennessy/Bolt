import os
import importlib


def find_plugins(path):
    for file in os.listdir(path):
        if not file.startswith('__'):
            if file.endswith(".py"):
                fullname = os.path.splitext(os.path.basename(file))[0]

                try:
                    module = importlib.machinery.SourceFileLoader(fullname, os.path.join(path, file)).load_module()
                except ImportError as e:
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
