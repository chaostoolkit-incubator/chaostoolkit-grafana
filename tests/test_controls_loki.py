# -*- coding: utf-8 -*-
import requests_mock
from chaoslib.run import EventHandlerRegistry
from logzero import logger

from chaosgrafana.controls.loki import configure_control


def test_sending_to_loki():
    with requests_mock.Mocker() as m:
        m.post("http://localhost.test:3100/loki/api/v1/push", status_code=204)

        registry = EventHandlerRegistry()
        configure_control(
            experiment={"title": "hello"},
            event_registry=registry,
            secrets={"auth": ("admin", "admin")},
            loki_endpoint="http://localhost.test:3100",
            tags={"test": "yes"},
        )

        logger.error("hello")

    assert m.called
    payload = m.request_history[0].json()
    stream = payload["streams"][0]["stream"]
    assert stream["test"] == "yes"
    assert "chaostoolkit_lib_version" in stream
    assert "chaostoolkit_run_id" in stream
    assert "chaostoolkit_experiment_title" in stream
    assert stream["source"] == "chaostoolkit"
