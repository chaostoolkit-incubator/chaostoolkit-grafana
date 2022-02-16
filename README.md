# Grafana extension for the Chaos Toolkit Extension

[![Version](https://img.shields.io/pypi/v/chaostoolkit-grafana.svg)](https://img.shields.io/pypi/v/chaostoolkit-grafana.svg)
[![License](https://img.shields.io/pypi/l/chaostoolkit-grafana.svg)](https://img.shields.io/pypi/l/chaostoolkit-grafana.svg)

[![Build](https://github.com/chaostoolkit-incubator/chaostoolkit-grafana/actions/workflows/build.yaml/badge.svg)](https://github.com/chaostoolkit-incubator/chaostoolkit-grafana/actions/workflows/build.yaml)
[![codecov](https://codecov.io/gh/chaostoolkit-incubator/chaostoolkit-grafana/branch/master/graph/badge.svg)](https://codecov.io/gh/chaostoolkit-incubator/chaostoolkit-grafana)
[![Python versions](https://img.shields.io/pypi/pyversions/chaostoolkit-grafana.svg)](https://www.python.org/)

This project should be used as a starting point to create your own
Chaos Toolkit extension.

## Install

This package requires Python 3.7+

To be used from your experiment, this package must be installed in the Python
environment where [chaostoolkit][] already lives.

[chaostoolkit]: https://github.com/chaostoolkit/chaostoolkit

```
$ pip install chaostoolkit-grafana
```

## Usage

### Sending Chaos Toolkit logs to Loki

To send the Chaos Toolkit logs to Loki endpoints, you need to enable the
according control as follows:

```json
{
    "secrets": {
        "grafana": {
            "auth": ["admin", "admin"]
        }
    },
    "controls": [
        {
            "name": "loki",
            "provider": {
                "type": "python",
                "module": "chaosgrafana.controls.loki",
                "secrets": ["grafana"],
                "arguments": {
                    "loki_endpoint": "http://localhost:3100",
                    "tags": {"service": "something"}
                }
            }
        }
    ]
}
```

## Test

To run the tests for the project execute the following:

```
$ make tests
```

### Formatting and Linting

We use a combination of [`black`][black], [`flake8`][flake8], and [`isort`][isort]
to both lint and format this repositories code.

[black]: https://github.com/psf/black
[flake8]: https://github.com/PyCQA/flake8
[isort]: https://github.com/PyCQA/isort

Before raising a Pull Request, we recommend you run formatting against your
code with:

```console
$ make format
```

This will automatically format any code that doesn't adhere to the formatting
standards.

As some things are not picked up by the formatting, we also recommend you run:

```console
$ make lint
```

To ensure that any unused import statements/strings that are too long, etc.
are also picked up.

## Contribute

If you wish to contribute more functions to this package, you are more than
welcome to do so. Please, fork this project, make your changes following the
usual [PEP 8][pep8] code style, sprinkling with tests and submit a PR for
review.

[pep8]: https://pycodestyle.readthedocs.io/en/latest/
