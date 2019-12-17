[**Documentation**](https://docs.bolt.bot) | [**Issues**](https://github.com/ns-phennessy/Bolt/issues/new/choose) | [**Discord**](#)

---

## Table of Contents
1. [Report Bug](#report-bug)
2. [Suggest Feature](#suggest-feature)
3. [Submit Changes](#submit-changes)
4. [Discussion](#changes)
5. [Code Style](#code-style)
6. [Documentation](#documentation)
7. [Development Setup](#development-setup)
8. [Running Tests](#running-tests)
9. [Building Release Artifact](#building-release-artifact)
10. [Versioning](#versioning)
11. [License](#license)


## Report Bug

[**Click here**](https://github.com/ns-phennessy/Bolt/issues/new/choose) to report a bug.

Please follow the template and provide as much information as possible.


## Suggest Feature

[**Click here**](https://github.com/ns-phennessy/Bolt/issues/new/choose) to suggest a feature addition.

Please follow the template and provide as much information as possible.

Pull requests that implement the feature are welcomed.


## Submit Changes

TODO How to do a PR


## Code Style

This project adheres to [pep8](https://www.python.org/dev/peps/pep-0008/) with the
notable exception line length is irrelevant. Almost all lines in project are under 100 characters, but are not nessessarily restricted to that.

The ability to comprehend the code is the only thing that matters.


## Documentation

Link: [**https://docs.bolt.bot**](https://docs.bolt.bot)

This project uses [Gitbook](gitbook.com) for documentation,
backed by Github in this repo's `/docs` directory. 

The documentation is targeted at a developer using Bolt. 

**Documentation Goals**:
- Users should experience success in < 30 minutes
- Ability to dive into advanced usage
- Reference
    - Function interfaces
    - Constants


## Setup Development Environment

This project uses [pipenv](https://github.com/pypa/pipenv).

Install pipenv then run:
```bash
$ pipenv install --dev
```


## Run Tests

Make sure your [development environment](#setup-development-environment) is setup.

```bash
$ pipenv run tests
```


## Build Release Artifact

Bolt can be distributed bundles:
- RPM
- DEB
- TAR.GZ
- Docker

Scripts exist to do this automatically. 

Make sure your [development environment](#setup-development-environment) is setup.

```bash
$ pipenv run build [RPM|DEB|TAR|BIN|DOCKER]
```

## Versioning

This project follows the [semver](https://semver.org/) standard.

This project uses [bumpversion](https://github.com/peritus/bumpversion) to automatically
bump the version, set the version string in certain files, adds git tags and special bump version commits.

```bash
$ pipenv run bump [major|minor|patch]
```

When to bump:
- **Major**: Backward-incompatible changes, feature deletion, or depecration. *This should happen sparingly*
- **Minor**: New features or enhancements
- **Patch**: Bug fixes, documentation updates, security patches


## License

By contributing, you agree that your contributions will be licensed under the [MIT License](https://github.com/ns-phennessy/Bolt/blob/master/LICENSE.txt).
