from unittest.mock import ANY, patch

from chaosgrafana.k6.actions import run_script, stress_endpoint

from . import MockSubprocessContext, full_plugin_path


@patch("subprocess.Popen")
@patch.dict("chaosgrafana.k6.driver.os.environ", clear=True)
def test_run_script(mocked_popen):
    mocked_popen.return_value = MockSubprocessContext(returncode=None)

    result = run_script(
        script_path="../myscript.js",
        vus=5,
        duration="10m",
        debug=True,
    )

    assert result is True
    mocked_popen.assert_called_once_with(
        [
            "k6",
            "run",
            "--quiet",
            "--vus",
            "5",
            "--duration",
            "10m",
            "../myscript.js",
        ],
        stderr=ANY,
        stdout=ANY,
        env={},
    )


@patch("subprocess.Popen")
@patch.dict(
    "chaosgrafana.k6.driver.os.environ",
    {"TEST": "original", "OTHER": "123"},
    clear=True,
)
def test_run_script_env_overrides(mocked_popen):
    mocked_popen.return_value = MockSubprocessContext(returncode=None)

    result = run_script(
        script_path="../myscript.js",
        vus=5,
        duration="10m",
        debug=True,
        environ={"TEST": "newvalue"},
    )

    assert result is True
    mocked_popen.assert_called_once_with(
        [
            "k6",
            "run",
            "--quiet",
            "--vus",
            "5",
            "--duration",
            "10m",
            "../myscript.js",
        ],
        stderr=ANY,
        stdout=ANY,
        env={"TEST": "newvalue", "OTHER": "123"},
    )


@patch("subprocess.Popen")
@patch.dict("chaosgrafana.k6.driver.os.environ", clear=True)
def test_run_script_stages(mocked_popen):
    mocked_popen.return_value = MockSubprocessContext(returncode=None)

    result = run_script(
        script_path="../myscript.js",
        stages=[
            {"duration": "10m", "target": 10},
            {"duration": "5m", "target": 50},
            {"duration": "1h10m2s", "target": 100},
        ],
        debug=True,
    )

    assert result is True
    mocked_popen.assert_called_once_with(
        [
            "k6",
            "run",
            "--quiet",
            "--stage",
            "10m:10",
            "--stage",
            "5m:50",
            "--stage",
            "1h10m2s:100",
            "../myscript.js",
        ],
        stderr=ANY,
        stdout=ANY,
        env={},
    )


@patch("subprocess.Popen")
@patch.dict("chaosgrafana.k6.driver.os.environ", clear=True)
def test_run_script_iterations(mocked_popen):
    mocked_popen.return_value = MockSubprocessContext(returncode=None)

    result = run_script(
        script_path="../myscript.js",
        vus=2,
        duration="10m",
        iterations=10,
        debug=True,
    )

    assert result is True
    mocked_popen.assert_called_once_with(
        [
            "k6",
            "run",
            "--quiet",
            "--iterations",
            "10",
            "--vus",
            "2",
            "../myscript.js",
        ],
        stderr=ANY,
        stdout=ANY,
        env={},
    )


@patch("subprocess.Popen")
@patch.dict("chaosgrafana.k6.driver.os.environ", clear=True)
def test_stress_endpoint(mocked_popen):
    mocked_popen.return_value = MockSubprocessContext(returncode=None)

    result = stress_endpoint(
        endpoint="http://localhost:3000",
        vus=100,
        duration="10m",
        debug=True,
    )

    js_path = full_plugin_path("k6/scripts/single-endpoint.js")

    assert result is True
    mocked_popen.assert_called_once_with(
        ["k6", "run", "--quiet", "--vus", "100", "--duration", "10m", js_path],
        stderr=ANY,
        stdout=ANY,
        env={"CHAOS_K6_URL": "http://localhost:3000"},
    )
