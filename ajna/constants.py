from decimal import Decimal

SECONDS_PER_YEAR = 31536000

# Grant proposal periods
CHALLENGE_PERIOD_LENGTH = 50400  # 7 days
FUNDING_PERIOD_LENGTH = 72000  # 10 days
SCREENING_PERIOD_LENGTH = 525600  # 73 days

MAX_PRICE = 1004968987606512354182109771
MAX_PRICE_DECIMAL = Decimal("1004968987.606512354182109771")
MAX_INFLATED_PRICE = Decimal("50248449380.32561770910548855")

AJNA_DEPLOYMENTS = {
    "v2": ["ethereum", "goerli"],
    "v3": ["ethereum", "goerli", "base", "arbitrum", "optimism", "polygon"],
}


ERC20 = "erc20"
ERC721 = "erc721"

ERC_CHOICES = [(ERC20, ERC20), (ERC721, ERC721)]
