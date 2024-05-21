from ajna.v4.arbitrum.models import *  # noqa: F403
from ajna.v4.base.models import *  # noqa: F403
from ajna.v4.blast.models import *  # noqa: F403
from ajna.v4.ethereum.models import *  # noqa: F403
from ajna.v4.filecoin.models import *  # noqa: F403
from ajna.v4.gnosis.models import *  # noqa: F403
from ajna.v4.optimism.models import *  # noqa: F403
from ajna.v4.polygon.models import *  # noqa: F403

from ..models import base


class V4NetworkStatsDaily(base.NetworkStatsDaily):
    pass


class V4OverallStats(base.OverallStats):
    pass
