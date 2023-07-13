from tests import factories


class V1GoerliRemoveCollateralFactory(factories.RemoveCollateralFactory):
    class Meta:
        model = "ajna.V1GoerliRemoveCollateral"


class V1GoerliAddCollateralFactory(factories.AddCollateralFactory):
    class Meta:
        model = "ajna.V1GoerliAddCollateral"


class V1GoerliAddQuoteTokenFactory(factories.AddQuoteTokenFactory):
    class Meta:
        model = "ajna.V1GoerliAddQuoteToken"


class V1GoerliRemoveQuoteTokenFactory(factories.RemoveQuoteTokenFactory):
    class Meta:
        model = "ajna.V1GoerliRemoveQuoteToken"


class V1GoerliDrawDebtFactory(factories.DrawDebtFactory):
    class Meta:
        model = "ajna.V1GoerliDrawDebt"


class V1GoerliRepayDebtFactory(factories.RepayDebtFactory):
    class Meta:
        model = "ajna.V1GoerliRepayDebt"
