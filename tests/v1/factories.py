from tests import factories


class V1PoolFactory(factories.PoolFactory):
    class Meta:
        model = "ajna.V1EthereumPool"


class V1DrawDebtFactory(factories.DrawDebtFactory):
    class Meta:
        model = "ajna.V1EthereumDrawDebt"


class V1RepayDebtFactory(factories.RepayDebtFactory):
    class Meta:
        model = "ajna.V1EthereumRepayDebt"


class V1AddQuoteTokenFactory(factories.AddQuoteTokenFactory):
    class Meta:
        model = "ajna.V1EthereumAddQuoteToken"


class V1RemoveQuoteTokenFactory(factories.RemoveQuoteTokenFactory):
    class Meta:
        model = "ajna.V1EthereumRemoveQuoteToken"


class V1MoveQuoteTokenFactory(factories.MoveQuoteTokenFactory):
    class Meta:
        model = "ajna.V1EthereumMoveQuoteToken"


class V1AddCollateralFactory(factories.AddCollateralFactory):
    class Meta:
        model = "ajna.V1EthereumAddCollateral"


class V1RemoveCollateralFactory(factories.RemoveCollateralFactory):
    class Meta:
        model = "ajna.V1EthereumRemoveCollateral"


class V1TokenFactory(factories.TokenFactory):
    class Meta:
        model = "ajna.V1EthereumToken"


class V1BucketFactory(factories.BucketFactory):
    class Meta:
        model = "ajna.V1EthereumBucket"
