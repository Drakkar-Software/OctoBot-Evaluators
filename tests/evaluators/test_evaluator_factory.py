#  Drakkar-Software OctoBot-Evaluators
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
import pytest

import octobot_tentacles_manager.api as tentacles_api
import octobot_evaluators.evaluators as evaluators
import octobot_commons.enums as enums
import octobot_commons.symbol_util as symbol_util
from tests import event_loop, matrix_id, install_tentacles, evaluators_and_matrix_channels

pytestmark = pytest.mark.asyncio

exchange_name = "TEST_EXCHANGE_NAME"
bot_id = "TEST_BOT_ID"
symbols_by_crypto_currencies = {
    "Bitcoin": ["BTC/USDT"],
    "Ethereum": ["ETH/USD", "ETH/BTC"]
}
symbols = ["BTC/USDT", "ETH/USD", "ETH/BTC"]
time_frames = [enums.TimeFrames.ONE_HOUR, enums.TimeFrames.FOUR_HOURS]

crypto_currency_name_by_crypto_currencies = {}
symbols_by_crypto_currency_tickers = {}
for name, symbol_list in symbols_by_crypto_currencies.items():
    ticker = symbol_util.split_symbol(symbol_list[0])[0]
    crypto_currency_name_by_crypto_currencies[ticker] = name
    symbols_by_crypto_currency_tickers[ticker] = symbol_list


@pytest.mark.usefixtures("event_loop", "install_tentacles")
async def test_create_all_type_evaluators(evaluators_and_matrix_channels):
    tentacles_setup_config = tentacles_api.get_tentacles_setup_config()
    created_evaluators = await evaluators.create_all_type_evaluators(tentacles_setup_config,
                                                                     matrix_id=evaluators_and_matrix_channels,
                                                                     exchange_name=exchange_name,
                                                                     bot_id=bot_id,
                                                                     symbols_by_crypto_currencies=symbols_by_crypto_currencies,
                                                                     symbols=symbols,
                                                                     time_frames=time_frames)

    assert not created_evaluators  # Trading package is not installed


@pytest.mark.usefixtures("event_loop", "install_tentacles")
async def test_create_strategy_evaluators(evaluators_and_matrix_channels):
    import tentacles
    await _test_evaluators_creation(evaluators.StrategyEvaluator, evaluators_and_matrix_channels, [
        tentacles.SimpleStrategyEvaluator,
        tentacles.DipAnalyserStrategyEvaluator,
        tentacles.MoveSignalsStrategyEvaluator
    ])


@pytest.mark.usefixtures("event_loop", "install_tentacles")
async def test_create_ta_evaluators(evaluators_and_matrix_channels):
    import tentacles
    await _test_evaluators_creation(evaluators.TAEvaluator, evaluators_and_matrix_channels, [
        tentacles.RSIMomentumEvaluator,
        tentacles.ADXMomentumEvaluator,
        tentacles.StochasticRSIVolatilityEvaluator
    ])


@pytest.mark.usefixtures("event_loop", "install_tentacles")
async def test_create_social_evaluators(evaluators_and_matrix_channels):
    import tentacles
    await _test_evaluators_creation(evaluators.SocialEvaluator, evaluators_and_matrix_channels, [
        tentacles.RedditForumEvaluator
    ])


@pytest.mark.usefixtures("event_loop", "install_tentacles")
async def test_create_rt_evaluators(evaluators_and_matrix_channels):
    import tentacles
    await _test_evaluators_creation(evaluators.RealTimeEvaluator, evaluators_and_matrix_channels, [
        tentacles.InstantFluctuationsEvaluator
    ])


async def _test_evaluators_creation(evaluator_parent_class, fixture_matrix_id, expected_evaluators):
    tentacles_setup_config = tentacles_api.get_tentacles_setup_config()
    created_evaluators = await evaluators.create_evaluators(evaluator_parent_class=evaluator_parent_class,
                                                            tentacles_setup_config=tentacles_setup_config,
                                                            matrix_id=fixture_matrix_id,
                                                            exchange_name=exchange_name,
                                                            bot_id=bot_id,
                                                            crypto_currency_name_by_crypto_currencies=crypto_currency_name_by_crypto_currencies,
                                                            symbols_by_crypto_currency_tickers=symbols_by_crypto_currency_tickers,
                                                            symbols=symbols,
                                                            time_frames=time_frames)
    assert created_evaluators
    assert all([evaluator.__class__ in expected_evaluators for evaluator in created_evaluators])
