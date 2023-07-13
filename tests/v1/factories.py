from tests import factories


class V1TokenFactory(factories.TokenFactory):
    class Meta:
        model = "ajna.V1EthereumToken"


class V1BucketFactory(factories.BucketFactory):
    class Meta:
        model = "ajna.V1EthereumBucket"


class V1PoolFactory(factories.PoolFactory):
    class Meta:
        model = "ajna.V1EthereumPool"


def generate_pools(number=3):
    for _ in range(0, number):
        pools = V1PoolFactory.create_batch(3)
        for pool in pools:
            V1TokenFactory.create(underlying_address=pool.collateral_token_address)
            V1TokenFactory.create(underlying_address=pool.quote_token_address)
