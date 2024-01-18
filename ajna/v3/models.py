from ajna.v3.arbitrum.models import *  # noqa
from ajna.v3.base.models import *  # noqa
from ajna.v3.ethereum.models import *  # noqa
from ajna.v3.goerli.models import *  # noqa
from ajna.v3.optimism.models import *  # noqa
from ajna.v3.polygon.models import *  # noqa

from ..models import base


class V3NetworkStatsDaily(base.NetworkStatsDaily):
    pass


class V3OverallStats(base.OverallStats):
    pass
