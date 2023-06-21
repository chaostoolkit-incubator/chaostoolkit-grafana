from unittest.mock import ANY, patch

from chaosgrafana.k6.probes import http

from . import MockSubprocessContext, full_plugin_path


@patch("subprocess.Popen")
@patch.dict("chaosgrafana.k6.probes.os.environ", clear=True)
def test_http(mocked_popen):
    mocked_popen.return_value = MockSubprocessContext(returncode=None)

    result = http(
        endpoint="http://localhost:3000",
        method="POST",
        status=201,
        vus=5,
        duration="10s",
        timeout=3,
    )

    js_path = full_plugin_path("k6/scripts/probe.js")

    expected_env = {
        "CHAOS_K6_URL": "http://localhost:3000",
        "CHAOS_K6_METHOD": "POST",
        "CHAOS_K6_STATUS": "201",
        "CHAOS_K6_BODY": "",
        "CHAOS_K6_HEADERS": "{}",
        "CHAOS_K6_VUS": "5",
        "CHAOS_K6_DURATION": "10s",
        "CHAOS_K6_HTTP_TIMEOUT": "3",
    }
    assert result is True
    mocked_popen.assert_called_once_with(
        ["k6", "run", "--quiet", js_path],
        stderr=ANY,
        stdout=ANY,
        env=expected_env,
    )
