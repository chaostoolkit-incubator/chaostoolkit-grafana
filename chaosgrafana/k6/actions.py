import os
from pathlib import Path
from typing import Dict, List

from logzero import logger

from .driver import K6, GenericOpt, Stage

__all__ = ["run_script", "stress_endpoint"]


def run_script(
    script_path: str = None,
    vus: int = 1,
    duration: str = "1s",
    stages: List[Dict] = None,
    iterations: int = None,
    log_file: str = None,
    debug: bool = False,
    environ: Dict = None,
):
    """
    Run an arbitrary k6 script with a configurable amount of VUs and duration.
    Depending on the specs of the attacking machine, possible VU amount may
    vary.
    For a non-customized 2019 Macbook Pro, it will cap around 250 +/- 50.

    Parameters
    ----------
    script_path : str
      Full path to the k6 test script
    vus : int
      Amount of virtual users to run the test with
    duration : str
      Duration, written as a string, ie: `1h2m3s` etc
    stages: list
      The list of test stages, with duration and target vus
    iterations: int
      Run test script only for a certain number of iterations
    log_file: str
      (Optional) Relative path to the file where output should be logged.
    environ: dict
      (Optional) Environment override used when running the script
    """
    logger.info("Running " + script_path)
    driver = K6(debug=debug, log_file=log_file, environ=environ)

    if iterations:
        duration = None
        driver.add_options(GenericOpt("--iterations", iterations))
    if stages:
        duration = None
        vus = None
        for stage in stages:
            driver.add_options(
                Stage(stage.get("duration"), stage.get("target"))
            )
    if vus:
        driver.add_options(GenericOpt("--vus", vus))
    if duration:
        driver.add_options(GenericOpt("--duration", duration))

    return driver.run_script(script_path)


def stress_endpoint(
    endpoint: str = None,
    vus: int = 1,
    duration: str = "1s",
    log_file: str = None,
    debug: bool = False,
):
    """
    Stress a single endpoint with a configurable amount of VUs and duration.
    Depending on the specs of the attacking machine, possible VU amount may
    vary.
    For a non-customized 2019 Macbook Pro, it will cap around 250 +/- 50.

    Parameters
    ----------
    endpoint : str
      The URL to the endpoint you want to stress, including the scheme prefix.
    vus : int
      Amount of virtual users to run the test with
    duration : str
      Duration, written as a string, ie: `1h2m3s` etc
    log_file: str
      (Optional) Relative path to the file where output should be logged.
    """
    base_path = Path(__file__).parent
    js_path = str(base_path.parent) + "/k6/scripts"

    logger.info(
        'Stressing the endpoint "{}" with {} VUs for {}.'.format(
            endpoint, vus, duration
        )
    )

    env = dict(**os.environ, CHAOS_K6_URL=endpoint)
    driver = K6(debug=debug, log_file=log_file, environ=env)
    driver.add_options(
        GenericOpt("--vus", vus),
        GenericOpt("--duration", duration),
    )
    result = driver.run_script(js_path + "/single-endpoint.js")

    logger.info("Stressing completed.")
    if log_file is not None:
        logger.info("Logged K6 output to {}.".format(log_file))
    return result
