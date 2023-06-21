import json
import os

from .driver import K6

__all__ = ["http"]


def http(
    endpoint: str,
    method: str = "GET",
    status: int = 200,
    body: str = "",
    headers: dict = {},
    vus: int = 1,
    duration: str = "",
    debug: bool = False,
    timeout: int = 1,
) -> bool:
    """
    Probe an endpoint to make sure it responds to an http request
    with the expected HTTP status code. Depending on the endpoint and your
    payload, this action might be destructive. Use with caution.

    Parameters
    ----------
    endpoint : str
        The URL to the endpoint to probe
    method : str
        A valid http request method name, like GET, POST, PUT, DELETE, OPTIONS, or PATCH
    status : int
        The expected HTTP Response status code.
    vus : int
        The amount of concurrent virtual users accessing the endpoint
    duration : str
        How long to probe the endpoint. Expressed as a duration string,
        i.e "20s", "1m", "1h" etc.
    timeout : int
        Timeout duration for http requests. Defaults to 1 second
    """  # noqa: E501
    if status < 100 or status > 999:
        raise ValueError("Invalid HTTP Response status code expection")
    if method.lower() not in [
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "options",
    ]:
        raise ValueError("Invalid HTTP Request method")
    if endpoint is None:
        raise ValueError("Endpoint is a required argument")

    env = dict(
        CHAOS_K6_URL=endpoint,
        CHAOS_K6_METHOD=method,
        CHAOS_K6_STATUS=str(status),
        CHAOS_K6_BODY=body,
        CHAOS_K6_HEADERS=json.dumps(headers),
        CHAOS_K6_VUS=str(vus),
        CHAOS_K6_DURATION=duration,
        CHAOS_K6_HTTP_TIMEOUT=str(timeout),
    )

    scripts_path = os.path.dirname(os.path.realpath(__file__))

    js_path = f"{scripts_path}/scripts/probe.js"

    driver = K6(debug=debug, environ=env)
    return driver.run_script(js_path)
