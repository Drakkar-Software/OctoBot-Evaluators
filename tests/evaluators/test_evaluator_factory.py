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
import mock

import octobot_tentacles_manager.api as tentacles_api
import octobot_evaluators.evaluators as evaluators
import octobot_commons.enums as enums
import octobot_commons.symbol_util as symbol_util
from tests import event_loop, matrix_id, install_tentacles, evaluators_and_matrix_channels
from octobot_evaluators.evaluators.evaluator_factory import _extract_traded_pairs, _filter_pairs

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

    # mock start method to prevent side effects (octobot-trading imports, etc)
    with mock.patch.object(evaluator_parent_class, "start", mock.AsyncMock()):
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


async def test_extract_traded_pairs():
    exchange_name = "binance"
    matrix_id = "id"
    exchange_api = ExchangeAPIMock()

    # no symbol config
    symbols_by_crypto_currencies = None
    crypto_currency_name_by_crypto_currencies, symbols_by_crypto_currency_tickers = \
        _extract_traded_pairs(symbols_by_crypto_currencies, exchange_name, matrix_id, exchange_api)
    assert crypto_currency_name_by_crypto_currencies == {}
    assert symbols_by_crypto_currency_tickers == {}

    # normal symbol config
    symbols_by_crypto_currencies = {
        'AAVE': ['AAVE/BTC', 'AAVE/USDT'],
        'Cardano': ['ADA/BTC']
    }
    crypto_currency_name_by_crypto_currencies, symbols_by_crypto_currency_tickers = \
        _extract_traded_pairs(symbols_by_crypto_currencies, exchange_name, matrix_id, exchange_api)
    assert crypto_currency_name_by_crypto_currencies == {
        'AAVE': 'AAVE',
        'ADA': 'Cardano'
    }
    assert symbols_by_crypto_currency_tickers == {
        'AAVE': {'AAVE/BTC', 'AAVE/USDT'},
        'ADA': {'ADA/BTC'}
    }

    # AAVE/USDT in Cardano symbol config
    symbols_by_crypto_currencies = {
        'AAVE': ['AAVE/BTC'],
        'Cardano': ['AAVE/USDT', 'ADA/BTC']
    }
    crypto_currency_name_by_crypto_currencies, symbols_by_crypto_currency_tickers = \
        _extract_traded_pairs(symbols_by_crypto_currencies, exchange_name, matrix_id, exchange_api)
    assert crypto_currency_name_by_crypto_currencies == {
        'AAVE': 'AAVE',
        'ADA': 'Cardano'
    }
    assert symbols_by_crypto_currency_tickers == {
        'AAVE': {'AAVE/BTC', 'AAVE/USDT'},
        'ADA': {'ADA/BTC'}
    }

    # Many symbol config by reference market
    symbols_by_crypto_currencies = {
        'Bitcoin': [
            'AAVE/BTC', 'ADA/BTC', 'ATOM/BTC', 'BAT/BTC', 'BNB/BTC', 'DASH/BTC', 'DOT/BTC',
            'EOS/BTC', 'ETC/BTC', 'ETH/BTC', 'FIL/BTC', 'LINK/BTC', 'LTC/BTC', 'NEO/BTC',
            'ONT/BTC', 'ROSE/BTC', 'SUSHI/BTC', 'SXP/BTC', 'THETA/BTC', 'TOMO/BTC', 'UNI/BTC',
            'WAN/BTC', 'XLM/BTC', 'XMR/BTC', 'XTZ/BTC', 'YFI/BTC'
        ],
        'Tether': [
            'AAVE/USDT', 'ADA/USDT', 'ATOM/USDT', 'BAT/USDT', 'BNB/USDT', 'BTC/USDT',
            'DASH/USDT', 'DOT/USDT', 'EOS/USDT', 'ETC/USDT', 'ETH/USDT', 'FIL/USDT',
            'LINK/USDT', 'LTC/USDT', 'NEO/USDT', 'ONT/USDT', 'ROSE/USDT', 'SUSHI/USDT',
            'SXP/USDT', 'THETA/USDT', 'TOMO/USDT', 'UNI/USDT', 'WAN/USDT', 'XLM/USDT',
            'XMR/USDT', 'XTZ/USDT', 'YFI/USDT'
        ]
    }
    crypto_currency_name_by_crypto_currencies, symbols_by_crypto_currency_tickers = \
        _extract_traded_pairs(symbols_by_crypto_currencies, exchange_name, matrix_id, exchange_api)
    assert crypto_currency_name_by_crypto_currencies == {
        'AAVE': 'Bitcoin', 'ADA': 'Bitcoin', 'ATOM': 'Bitcoin',
        'BAT': 'Bitcoin', 'BNB': 'Bitcoin', 'DASH': 'Bitcoin',
        'DOT': 'Bitcoin', 'EOS': 'Bitcoin', 'ETC': 'Bitcoin',
        'ETH': 'Bitcoin', 'FIL': 'Bitcoin', 'LINK': 'Bitcoin',
        'LTC': 'Bitcoin', 'NEO': 'Bitcoin', 'ONT': 'Bitcoin',
        'ROSE': 'Bitcoin', 'SUSHI': 'Bitcoin', 'SXP': 'Bitcoin',
        'THETA': 'Bitcoin', 'TOMO': 'Bitcoin', 'UNI': 'Bitcoin',
        'WAN': 'Bitcoin', 'XLM': 'Bitcoin', 'XMR': 'Bitcoin',
        'XTZ': 'Bitcoin', 'YFI': 'Bitcoin', 'BTC': 'Tether'
    }
    assert symbols_by_crypto_currency_tickers == {
        'AAVE': {'AAVE/BTC', 'AAVE/USDT'}, 'ADA': {'ADA/BTC', 'ADA/USDT'}, 'ATOM': {'ATOM/BTC', 'ATOM/USDT'},
        'BAT': {'BAT/BTC', 'BAT/USDT'}, 'BNB': {'BNB/USDT', 'BNB/BTC'}, 'DASH': {'DASH/USDT', 'DASH/BTC'},
        'DOT': {'DOT/BTC', 'DOT/USDT'}, 'EOS': {'EOS/BTC', 'EOS/USDT'}, 'ETC': {'ETC/USDT', 'ETC/BTC'},
        'ETH': {'ETH/USDT', 'ETH/BTC'}, 'FIL': {'FIL/BTC', 'FIL/USDT'}, 'LINK': {'LINK/USDT', 'LINK/BTC'},
        'LTC': {'LTC/USDT', 'LTC/BTC'}, 'NEO': {'NEO/USDT', 'NEO/BTC'}, 'ONT': {'ONT/BTC', 'ONT/USDT'},
        'ROSE': {'ROSE/USDT', 'ROSE/BTC'}, 'SUSHI': {'SUSHI/USDT', 'SUSHI/BTC'}, 'SXP': {'SXP/BTC', 'SXP/USDT'},
        'THETA': {'THETA/USDT', 'THETA/BTC'}, 'TOMO': {'TOMO/BTC', 'TOMO/USDT'}, 'UNI': {'UNI/BTC', 'UNI/USDT'},
        'WAN': {'WAN/BTC', 'WAN/USDT'}, 'XLM': {'XLM/USDT', 'XLM/BTC'}, 'XMR': {'XMR/BTC', 'XMR/USDT'},
        'XTZ': {'XTZ/BTC', 'XTZ/USDT'}, 'YFI': {'YFI/USDT', 'YFI/BTC'}, 'BTC': {'BTC/USDT'}
    }


async def test_filter_pairs():
    exchange_api = ExchangeAPIMock()
    exchange_manager = None

    assert _filter_pairs(['BAT/BTC', 'BAT/USDT', 'BNB/USDT', 'BNB/BTC'], 'BAT', exchange_api, exchange_manager) == \
           {'BAT/BTC', 'BAT/USDT'}

    assert _filter_pairs(['BAT/BTC', 'BAT/USDT', 'BNB/USDT', 'BNB/BTC'], 'BNB', exchange_api, exchange_manager) == \
           {'BNB/BTC', 'BNB/USDT'}

    assert _filter_pairs(['BAT/BTC', 'BAT/USDT', 'BNB/USDT', 'BNB/BTC'], 'BTC', exchange_api, exchange_manager) == \
           set()

    assert _filter_pairs(['BAT/BTC', 'BAT/USDT', 'BNB/USDT', 'BNB/BTC'], 'USDT', exchange_api, exchange_manager) == \
           set()

    assert _filter_pairs([], 'USDT', exchange_api, exchange_manager) == \
           set()

    assert _filter_pairs([], 'USDT', exchange_api, exchange_manager) == \
           set()


class ExchangeAPIMock:

    def get_exchange_id_from_matrix_id(self, *args):
        return "1"

    def get_exchange_manager_from_exchange_name_and_id(self, *args):
        return None

    def get_base_currency(self, exchange_manager, symbol):
        return symbol_util.split_symbol(symbol)[0]
