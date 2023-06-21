""" A Chaos Toolkit driver to run Grafana K6 commands """
import os
import subprocess
from itertools import chain
from typing import Dict, List

from logzero import logger


def _run(
    *cmd: List[List[str]],
    log_file: str = None,
    debug: bool = False,
    environ: Dict = None,
):
    _cmd = list(chain(*cmd))

    context = dict(os.environ)
    if environ:
        context.update(environ)

    # Default output to the void
    pipeoutput = subprocess.DEVNULL
    # Use log file location if provided
    if log_file is not None:
        pipeoutput = open(log_file, "w")

    logger.info("Running Grafana k6 command: %s", " ".join(_cmd))

    with subprocess.Popen(
        _cmd,
        stderr=subprocess.STDOUT,
        stdout=None if debug is True else pipeoutput,
        env=context,
    ) as p:
        return p.returncode is None


class Stage:
    """Representation of a k6 command-line stage configuration"""

    def __init__(self, duration: str, target: int):
        self.duration = duration
        self.target = target

    def render(self) -> List[str]:
        return ["--stage", f"{str(self.duration)}:{self.target}"]


class GenericOpt:
    """Representation of a k6 generic command-line argument"""

    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    def render(self) -> List[str]:
        return [self.name, f"{str(self.value)}"]


class FlagOpt:
    """Representation of a k6 generic command-line flag"""

    def __init__(self, name: str):
        self.name = name

    def render(self) -> List[str]:
        return [self.name]


class K6:
    """Grafana k6 driver class"""

    def __init__(
        self, debug: bool = False, log_file: str = None, environ: Dict = None
    ):
        self.debug = debug
        self.log_file = log_file
        self.environ = environ
        self.options = []

    def add_options(self, *options):
        """Add command line options for k6 script execution"""
        if options:
            self.options.extend(options)

    def run_script(self, script) -> int:
        """
        Run the Grafana k6 script

        Parameters
        ----------
        script: str
            The load test script path
        """

        command = [
            "k6",
            "run",
            "--quiet",
        ]

        opts = []
        for opt in self.options:
            opts.extend(opt.render())

        return _run(
            command,
            opts,
            [script],
            log_file=self.log_file,
            environ=self.environ,
        )
