import logging
from datetime import date
from decimal import Decimal

from ajna.constants import AJNA_TOKEN_ADDRESS
from ajna.utils.wad import wad_to_decimal

from ..models import V3OverallStats

log = logging.getLogger(__name__)


def save_overall_ajna_burned(chain):
    calls = [
        (
            AJNA_TOKEN_ADDRESS,
            ["totalSupply()(uint256)"],
            ["totalSupply", None],
        ),
    ]
    data = chain.multicall(calls)
    total_supply = wad_to_decimal(data["totalSupply"])

    initial_supply = Decimal("1000000000")
    burned = initial_supply - total_supply

    V3OverallStats.objects.update_or_create(
        date=date.today(), defaults={"total_ajna_burned": burned}
    )
