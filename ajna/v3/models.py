from ajna.v3.arbitrum.models import *  # noqa: F403
from ajna.v3.base.models import *  # noqa: F403
from ajna.v3.optimism.models import *  # noqa: F403
from ajna.v3.polygon.models import *  # noqa: F403

from ..models import base


class V3NetworkStatsDaily(base.NetworkStatsDaily):
    pass


class V3OverallStats(base.OverallStats):
    pass
