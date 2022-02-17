import logging
import time
from secrets import token_hex
from typing import Any, Dict

import logging_loki
from chaoslib import __version__, experiment_hash
from chaoslib.run import EventHandlerRegistry, RunEventHandler
from chaoslib.types import Activity, Experiment, Journal, Run, Secrets
from logzero import logger as ctk_logger

__all__ = ["configure_control"]
DEFAULT_LOKI_URL = "http://localhost:3100"
loki_logger = logging.getLogger("chaostoolkit-loki")


def configure_control(
    experiment: Experiment,
    secrets: Secrets = None,
    event_registry: EventHandlerRegistry = None,
    loki_endpoint: str = DEFAULT_LOKI_URL,
    tags: Dict[str, str] = None,
    experiment_ref: str = None,
    trace_id: str = None,
) -> None:
    """
    Configure a Python logger that sends its messages to a Loki endpoint.

    * `loki_endpoint` is teh base url of your Loki service
    * `tags` a mapping of strings injected in all logs
    * `experiment_ref` a unique string identifying this experiment, if none
      is provided, a has of the experiment is created
    * `trace_id` a unique string for a particular run of the experiment, if
      none is provided, a random string is generated

    This sends logs about the run events (started, finished, failed, etc.)
    """
    ctk_logger.debug("Add Loki handler to logger")

    if event_registry is None:
        ctk_logger.debug(
            "You may be using an older version of chaostoolkit-lib, make sure "
            "you run at least 1.26.0. The Grafana extension will not "
            "be enabled"
        )
        return

    url = f"{loki_endpoint}/loki/api/v1/push"
    auth = secrets.get("auth")
    experiment_ref = experiment_ref or experiment_hash(experiment)
    trace_id = trace_id or token_hex(16)
    tags = tags or {}
    tags.update(
        {
            "source": "chaostoolkit",
            "chaostoolkit_lib_version": __version__,
            "chaostoolkit_run_trace_id": trace_id,
            "chaostoolkit_experiment_ref": experiment_ref,
        }
    )

    experiment_tags = experiment.get("tags")
    if experiment_tags:
        tags.update(experiment_tags)

    logging_loki.emitter.LokiEmitter.level_tag = "level"
    handler = logging_loki.LokiHandler(
        url=url, tags=tags, auth=auth, version="1"
    )
    handler.emitter = FixedLokiEmitterV1(url, tags, auth)
    handler.setLevel(logging.INFO)
    loki_logger.addHandler(handler)
    loki_logger.setLevel(logging.INFO)

    event_registry.register(LokiRunEventHandler())

    loki_logger.info(
        "Experiment started",
        extra={
            "tags": {
                "type": "experiment-started",
                "title": experiment.get("title"),
            }
        },
    )


def before_activity_control(context: Activity, *args, **kwargs) -> None:
    a = context
    loki_logger.info(
        f"Activity '{a['name']}' started",
        extra={
            "tags": {"type": "experiment-activity-started", "name": a["name"]},
        },
    )


def after_activity_control(
    context: Activity, state: Run, *args, **kwargs
) -> None:
    a = context
    loki_logger.info(
        f"Activity '{a['name']}' finished",
        extra={
            "tags": {
                "type": "experiment-activity-finished",
                "name": a["name"],
                "status": state["status"],
                "start": state["start"],
                "end": state["end"],
                "duration": state["duration"],
                "output": state["output"],
                "exception": state.get("exception"),
            },
        },
    )


###############################################################################
# Private functions
###############################################################################
class FixedLokiEmitterV1(logging_loki.emitter.LokiEmitter):
    def build_payload(self, record: logging.LogRecord, line) -> dict:
        """Build JSON payload with a log entry."""
        labels = self.build_tags(record)
        ts = str(time.time_ns())
        stream = {
            "stream": labels,
            "values": [[ts, line]],
        }
        return {"streams": [stream]}


class LokiRunEventHandler(RunEventHandler):
    def finish(self, journal: Journal) -> None:
        loki_logger.info(
            "Experiment finished",
            extra={
                "tags": {
                    "type": "experiment-finished",
                    "deviated": journal.get("deviated"),
                    "status": journal.get("status"),
                    "start": journal.get("start"),
                    "end": journal.get("end"),
                    "duration": journal.get("duration"),
                },
            },
        )

    def interrupted(self, experiment: Experiment, journal: Journal) -> None:
        loki_logger.info(
            "Experiment interrupted",
            extra={"tags": {"type": "experiment-interrupted"}},
        )

    def signal_exit(self) -> None:
        loki_logger.info(
            "Experiment exit signal received",
            extra={"tags": {"type": "experiment-exit-signal"}},
        )

    def start_continuous_hypothesis(self, frequency: int) -> None:
        loki_logger.info(
            "Experiment steady state started running continuously",
            extra={"tags": {"type": "experiment-continuous-ssh-started"}},
        )

    def continuous_hypothesis_iteration(
        self, iteration_index: int, state: Any
    ) -> None:
        loki_logger.info(
            f"Experiment steady state iteration {iteration_index}",
            extra={
                "tags": {
                    "type": "experiment-continuous-ssh-iteration",
                    "iteration": iteration_index,
                }
            },
        )

    def continuous_hypothesis_completed(
        self,
        experiment: Experiment,
        journal: Journal,
        exception: Exception = None,
    ) -> None:
        loki_logger.info(
            "Experiment continuous steady state completed",
            extra={"tags": {"type": "experiment-continuous-ssh-completed"}},
        )

    def start_hypothesis_before(self, experiment: Experiment) -> None:
        loki_logger.info(
            "Experiment before steady state started",
            extra={"tags": {"type": "experiment-before-ssh-started"}},
        )

    def hypothesis_before_completed(
        self, experiment: Experiment, state: Dict[str, Any], journal: Journal
    ) -> None:
        extra = {
            "tags": {
                "type": "experiment-before-ssh-completed",
                "state_met": state.get("steady_state_met"),
            },
        }

        if state.get("steady_state_met") is False:
            for probe in state.get("probes", []):
                if probe["tolerance_met"] is False:
                    extra["tags"]["failed_probe"] = probe
                    break

        loki_logger.info(
            "Experiment before steady state completed", extra=extra
        )

    def start_hypothesis_after(self, experiment: Experiment) -> None:
        loki_logger.info(
            "Experiment after steady state started",
            extra={"tags": {"type": "experiment-after-ssh-started"}},
        )

    def hypothesis_after_completed(
        self, experiment: Experiment, state: Dict[str, Any], journal: Journal
    ) -> None:
        extra = {
            "tags": {
                "type": "experiment-after-ssh-completed",
                "state_met": state.get("steady_state_met"),
            },
        }

        if state.get("steady_state_met") is False:
            for probe in state.get("probes", []):
                if probe["tolerance_met"] is False:
                    extra["tags"]["failed_probe"] = probe
                    break

        loki_logger.info("Experiment after steady state completed", extra=extra)

    def start_method(self, experiment: Experiment) -> None:
        loki_logger.info(
            "Experiment method started",
            extra={"tags": {"type": "experiment-method-started"}},
        )

    def method_completed(self, experiment: Experiment, state: Any) -> None:
        loki_logger.info(
            "Experiment method completed",
            extra={"tags": {"type": "experiment-method-completed"}},
        )

    def start_rollbacks(self, experiment: Experiment) -> None:
        loki_logger.info(
            "Experiment rollbacks started",
            extra={"tags": {"type": "experiment-rollbacks-started"}},
        )

    def rollbacks_completed(
        self, experiment: Experiment, journal: Journal
    ) -> None:
        loki_logger.info(
            "Experiment rollbacks completed",
            extra={"tags": {"type": "experiment-rollbacks-completed"}},
        )

    def start_cooldown(self, duration: int) -> None:
        loki_logger.info(
            f"Experiment cooldown period started for {duration}s",
            extra={
                "tags": {
                    "type": "experiment-cooldown-started",
                    "duration": duration,
                }
            },
        )

    def cooldown_completed(self) -> None:
        loki_logger.info(
            "Experiment cooldown period completed",
            extra={"tags": {"type": "experiment-cooldown-completed"}},
        )
