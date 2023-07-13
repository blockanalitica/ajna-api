import pytest

from ajna.v1.goerli.tasks import (
    save_add_collateral_events_task,
    save_add_quote_token_events_tasks,
    save_draw_debts_events_tasks,
    save_remove_collateral_events_task,
    save_remove_quote_token_events_tasks,
    save_repay_debts_events_tasks,
)

from .factories import (
    V1GoerliAddCollateralFactory,
    V1GoerliAddQuoteTokenFactory,
    V1GoerliDrawDebtFactory,
    V1GoerliRemoveCollateralFactory,
    V1GoerliRemoveQuoteTokenFactory,
    V1GoerliRepayDebtFactory,
)


#########################################
# test_save_remove_collateral_events_task
#########################################
@pytest.mark.django_db
def test_save_remove_collateral_events_task(mocker):
    last_event = V1GoerliRemoveCollateralFactory(block_number=12345)

    func = mocker.patch("ajna.v1.goerli.tasks.fetch_and_save_remove_collaterals")
    save_remove_collateral_events_task()

    assert func.call_count == 1
    func_call_args = func.call_args_list[0][0]
    assert func_call_args[3] == last_event.block_number


@pytest.mark.django_db
def test_save_remove_collateral_events_task_empty(mocker):
    func = mocker.patch("ajna.v1.goerli.tasks.fetch_and_save_remove_collaterals")
    save_remove_collateral_events_task()

    assert func.call_count == 1
    func_call_args = func.call_args_list[0][0]
    assert func_call_args[3] == 0


#################################
# save_add_collateral_events_task
#################################
@pytest.mark.django_db
def test_save_add_collateral_events_task(mocker):
    last_event = V1GoerliAddCollateralFactory(block_number=12345)

    func = mocker.patch("ajna.v1.goerli.tasks.fetch_and_save_add_collaterals")
    save_add_collateral_events_task()

    assert func.call_count == 1
    func_call_args = func.call_args_list[0][0]
    assert func_call_args[3] == last_event.block_number


@pytest.mark.django_db
def test_save_add_collateral_events_task_empty(mocker):
    func = mocker.patch("ajna.v1.goerli.tasks.fetch_and_save_add_collaterals")
    save_add_collateral_events_task()

    assert func.call_count == 1
    func_call_args = func.call_args_list[0][0]
    assert func_call_args[3] == 0


###################################
# save_add_quote_token_events_tasks
###################################
@pytest.mark.django_db
def test_save_add_quote_token_events_tasks(mocker):
    last_event = V1GoerliAddQuoteTokenFactory(block_number=12345)

    func = mocker.patch("ajna.v1.goerli.tasks.fetch_and_save_add_quote_tokens")
    save_add_quote_token_events_tasks()

    assert func.call_count == 1
    func_call_args = func.call_args_list[0][0]
    assert func_call_args[3] == last_event.block_number


@pytest.mark.django_db
def test_save_add_quote_token_events_tasks_empty(mocker):
    func = mocker.patch("ajna.v1.goerli.tasks.fetch_and_save_add_quote_tokens")
    save_add_quote_token_events_tasks()

    assert func.call_count == 1
    func_call_args = func.call_args_list[0][0]
    assert func_call_args[3] == 0


######################################
# save_remove_quote_token_events_tasks
######################################
@pytest.mark.django_db
def test_save_remove_quote_token_events_tasks(mocker):
    last_event = V1GoerliRemoveQuoteTokenFactory(block_number=12345)

    func = mocker.patch("ajna.v1.goerli.tasks.fetch_and_save_remove_quote_tokens")
    save_remove_quote_token_events_tasks()

    assert func.call_count == 1
    func_call_args = func.call_args_list[0][0]
    assert func_call_args[3] == last_event.block_number


@pytest.mark.django_db
def test_save_remove_quote_token_events_tasks_empty(mocker):
    func = mocker.patch("ajna.v1.goerli.tasks.fetch_and_save_remove_quote_tokens")
    save_remove_quote_token_events_tasks()

    assert func.call_count == 1
    func_call_args = func.call_args_list[0][0]
    assert func_call_args[3] == 0


##############################
# save_draw_debts_events_tasks
##############################
@pytest.mark.django_db
def test_save_draw_debts_events_tasks(mocker):
    last_event = V1GoerliDrawDebtFactory(block_number=12345)

    func = mocker.patch("ajna.v1.goerli.tasks.fetch_and_save_draw_debts")
    save_draw_debts_events_tasks()

    assert func.call_count == 1
    func_call_args = func.call_args_list[0][0]
    assert func_call_args[3] == last_event.block_number


@pytest.mark.django_db
def test_save_draw_debts_events_tasks_empty(mocker):
    func = mocker.patch("ajna.v1.goerli.tasks.fetch_and_save_draw_debts")
    save_draw_debts_events_tasks()

    assert func.call_count == 1
    func_call_args = func.call_args_list[0][0]
    assert func_call_args[3] == 0


###############################
# save_repay_debts_events_tasks
###############################
@pytest.mark.django_db
def test_save_repay_debts_events_tasks(mocker):
    last_event = V1GoerliRepayDebtFactory(block_number=12345)

    func = mocker.patch("ajna.v1.goerli.tasks.fetch_and_save_repay_debts")
    save_repay_debts_events_tasks()

    assert func.call_count == 1
    func_call_args = func.call_args_list[0][0]
    assert func_call_args[3] == last_event.block_number


@pytest.mark.django_db
def test_save_repay_debts_events_tasks_empty(mocker):
    func = mocker.patch("ajna.v1.goerli.tasks.fetch_and_save_repay_debts")
    save_repay_debts_events_tasks()

    assert func.call_count == 1
    func_call_args = func.call_args_list[0][0]
    assert func_call_args[3] == 0
