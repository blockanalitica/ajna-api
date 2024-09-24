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
    "v2": ["ethereum"],
    "v3": ["base", "arbitrum", "optimism", "polygon"],
    "v4": [
        "ethereum",
        "base",
        "arbitrum",
        "optimism",
        "polygon",
        "blast",
        "gnosis",
        "mode",
        "rari",
    ],
}

AJNA_TOKEN_ADDRESS = "0x9a96ec9B57Fb64FbC60B423d1f4da7691Bd35079"  # noqa: S105

ERC20 = "erc20"
ERC721 = "erc721"

ERC_CHOICES = [(ERC20, ERC20), (ERC721, ERC721)]

ERC721_NON_SUBSET_HASH = "0x93e3b87db48beb11f82ff978661ba6e96f72f582300e9724191ab4b5d7964364"
