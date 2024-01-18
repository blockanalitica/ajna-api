from ajna.v4.arbitrum.models import *  # noqa
from ajna.v4.base.models import *  # noqa
from ajna.v4.ethereum.models import *  # noqa
from ajna.v4.goerli.models import *  # noqa
from ajna.v4.optimism.models import *  # noqa
from ajna.v4.polygon.models import *  # noqa

from ..models import base


class V4NetworkStatsDaily(base.NetworkStatsDaily):
    pass


class V4OverallStats(base.OverallStats):
    pass
