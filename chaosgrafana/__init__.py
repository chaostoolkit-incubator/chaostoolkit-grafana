# -*- coding: utf-8 -*-
from typing import List

from chaoslib.discovery.discover import (
    discover_activities,
    initialize_discovery_result,
)
from chaoslib.types import DiscoveredActivities, Discovery
from logzero import logger

__all__ = ["__version__", "create_k8s_api_client", "discover"]
__version__ = "0.1.2"


def discover(discover_system: bool = True) -> Discovery:
    """
    Discover Grafana capabilities offered by this extension.
    """
    logger.info("Discovering capabilities from chaostoolkit-grafana")

    discovery = initialize_discovery_result(
        "chaostoolkit-grafana", __version__, "grafana"
    )
    discovery["activities"].extend(load_exported_activities())
    return


###############################################################################
# Private functions
###############################################################################
def load_exported_activities() -> List[DiscoveredActivities]:
    """
    Extract metadata from actions and probes exposed by this extension.
    """
    activities = []
    activities.extend(
        discover_activities("chaosgrafana.controls.loki", "control")
    )
    return activities
