from setuptools import setup, find_packages

with open('REQUIREMENTS.txt') as file:
    requirements = file.read()

with open('VERSION.txt') as file:
    VERSION = file.read().strip('\n')

setup(
    name='arcbot',
    author='phennessy',
    url='https://github.com/ns-phennessy/Arcbot',
    version=VERSION,
    packages=find_packages(),
    license='GPLv3',
    description='Mechanical chat enrichment associate f or Discord',
    test_suite='tests',
    install_requires=requirements,
    setup_requires=[],
    tests_require=[]
)
