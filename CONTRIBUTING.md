# Setup dev enviornment

This project uses [pipenv](https://github.com/pypa/pipenv).

Install it then run:
```bash
$ pipenv install --dev
```

----------------------------------------------------------------------------------------
# Tests

```bash
$ pipenv run tests
```

----------------------------------------------------------------------------------------
# Building packages
Bolt can be distributed with a few different bundles:
- RPM
- DEB
- TAR.GZ
- Docker

Scripts exist to do this automatically.

## Building just the binary
This project uses [pex](https://github.com/pantsbuild/pex) to create a standalone
binary with all the dependencies included. It only requires a Python runtime to
execute.

```bash
$ pipenv run build binary
```

## Building RPM
```bash
$ pipenv run build rpm
```

## Building DEB
```bash
$ pipenv run build deb
```

## Building TARBALL
```bash
$ pipenv run build tarball
```

## Building Docker
```bash
$ pipenv run build docker
```

----------------------------------------------------------------------------------------
# Bump software version

This project follows the [semver](https://semver.org/) standard.
This project uses [bumpversion](https://github.com/peritus/bumpversion) to automatically
bump the version in various files, adds git tags and special bumped version commits.

```bash
$ pipenv run bump [major|minor|patch]
```

When to bump:
- **Major**: Backward-incompatible changes, feature deletion, or depecration. *This should happen sparingly*
- **Minor**: New features or enhancements
- **Patch**: Bug fixes, documentation updates, security patches


----------------------------------------------------------------------------------------
# Architecture
TODO


----------------------------------------------------------------------------------------
# Standards

This project adheres to [pep8](https://www.python.org/dev/peps/pep-0008/) with the
notable exception that the author does not care about line length. Almost all lines in
project are under 100 characters, but are not nessessarily restricted to that.

The ability to comprehend the code is the only thing that matters.

This project uses [Gitbook](gitbook.com) for documentation. The docs are managed in
Github in the `/docs` directory. The documentation is aimed at a consumer of the library
and tries to give users what they need to get going quickly.
    - Quick path to success
        - Users should experience success in <30 minutes
    - Ability to dive into advanced usage
    - Reference (what is the interface for a thing?)
