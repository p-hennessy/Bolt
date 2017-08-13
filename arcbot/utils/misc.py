import os
import importlib

def find_plugins(path):
    for file in os.listdir(path):
        if not file.startswith('__'):
            if file.endswith("Manage.py"):
                fullname = os.path.splitext(os.path.basename(file))[0]

                try:
                    module = importlib.machinery.SourceFileLoader(fullname, os.path.join(path, file)).load_module()
                except ImportError as e:
                    continue

                yield module



def Singleton(clazz):
    instance = clazz()
    instance.__call__ = lambda: instance
    return instance
