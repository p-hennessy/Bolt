from setuptools import setup, find_packages

with open('REQUIREMENTS.txt') as file:
    REQUIREMENTS = file.read()

with open('VERSION.txt') as file:
    VERSION = file.read().strip('\n')

setup(
    name='bolt',
    author='phennessy',
    url='https://github.com/ns-phennessy/Bolt',
    version=VERSION,
    packages=find_packages(),
    license='MIT',
    description='All the parts for building a Discord robot https://bolt.bot',
    test_suite='tests',
    install_requires=REQUIREMENTS,
    setup_requires=[],
    tests_require=[]
)
