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

import octobot_commons.tentacles_management as tentacles_management
import octobot_commons.constants as common_constants
import octobot_commons.logging as logging

import octobot_evaluators.api as api
import octobot_evaluators.evaluators as evaluator
import octobot_evaluators.constants as constants

LOGGER_NAME = "EvaluatorsFactory"


async def create_evaluators(evaluator_parent_class,
                            tentacles_setup_config: object,
                            matrix_id: str,
                            exchange_name: str,
                            bot_id: str,
                            crypto_currency_name_by_crypto_currencies: dict,
                            symbols_by_crypto_currency_tickers: dict,
                            symbols: list = None,
                            time_frames: list = None,
                            real_time_time_frames: list = None,
                            relevant_evaluators=common_constants.CONFIG_WILDCARD, ) -> list:
    return [
        await create_evaluator(evaluator_class,
                               tentacles_setup_config,
                               matrix_id=matrix_id,
                               exchange_name=exchange_name,
                               bot_id=bot_id,
                               cryptocurrency=cryptocurrency,
                               cryptocurrency_name=_get_cryptocurrency_name(
                                   evaluator_class,
                                   crypto_currency_name_by_crypto_currencies,
                                   cryptocurrency),
                               symbol=symbol,
                               time_frame=time_frame,
                               relevant_evaluators=relevant_evaluators,
                               all_symbols_by_crypto_currencies=symbols_by_crypto_currency_tickers,
                               time_frames=time_frames,
                               real_time_time_frames=real_time_time_frames
                               )
        for evaluator_class in tentacles_management.get_all_classes_from_parent(evaluator_parent_class)
        for cryptocurrency in _get_cryptocurrencies_to_create(evaluator_class,
                                                              crypto_currency_name_by_crypto_currencies)
        for symbol in _get_symbols_to_create(evaluator_class, symbols_by_crypto_currency_tickers,
                                             cryptocurrency, symbols)
        for time_frame in _get_time_frames_to_create(evaluator_class, time_frames)
    ]


def _get_cryptocurrency_name(evaluator_class, crypto_currency_name_by_crypto_currencies, cryptocurrency):
    return crypto_currency_name_by_crypto_currencies[cryptocurrency] \
        if crypto_currency_name_by_crypto_currencies \
           and cryptocurrency is not None \
           and not evaluator_class.get_is_cryptocurrency_name_wildcard() \
        else None


def _get_cryptocurrencies_to_create(evaluator_class, crypto_currency_name_by_crypto_currencies):
    return list(crypto_currency_name_by_crypto_currencies.keys()) \
        if crypto_currency_name_by_crypto_currencies and \
           not evaluator_class.get_is_cryptocurrencies_wildcard() else [None]


def _get_symbols_to_create(evaluator_class, symbols_by_crypto_currencies, cryptocurrency, symbols):
    currency_symbols = symbols
    if cryptocurrency is not None:
        currency_symbols = symbols_by_crypto_currencies[cryptocurrency] \
            if cryptocurrency in symbols_by_crypto_currencies else []
    return currency_symbols if currency_symbols and not evaluator_class.get_is_symbol_wildcard() else [None]


def _get_time_frames_to_create(evaluator_class, time_frames):
    return time_frames if time_frames and not evaluator_class.get_is_time_frame_wildcard() else [None]


async def create_evaluator(evaluator_class,
                           tentacles_setup_config: object,
                           matrix_id: str,
                           exchange_name: str,
                           bot_id: str,
                           cryptocurrency: str = None,
                           cryptocurrency_name: str = None,
                           symbol: str = None,
                           time_frame=None,
                           relevant_evaluators=common_constants.CONFIG_WILDCARD,
                           all_symbols_by_crypto_currencies=None,
                           time_frames=None,
                           real_time_time_frames=None):
    try:
        eval_class_instance = evaluator_class()
        eval_class_instance.set_tentacles_setup_config(tentacles_setup_config)
        if api.is_relevant_evaluator(eval_class_instance, relevant_evaluators):
            eval_class_instance.logger = logging.get_logger(evaluator_class.get_name())
            eval_class_instance.matrix_id = matrix_id
            eval_class_instance.exchange_name = exchange_name if exchange_name else None
            eval_class_instance.cryptocurrency = cryptocurrency
            eval_class_instance.cryptocurrency_name = cryptocurrency_name
            eval_class_instance.symbol = symbol if symbol else None
            eval_class_instance.time_frame = time_frame if time_frame else eval_class_instance.time_frame
            eval_class_instance.evaluator_type = evaluator.evaluator_class_str_to_matrix_type_dict[
                eval_class_instance.__class__.mro()[constants.EVALUATOR_CLASS_TYPE_MRO_INDEX].__name__]
            eval_class_instance.initialize(all_symbols_by_crypto_currencies, time_frames, real_time_time_frames)
            await eval_class_instance.prepare()
            # handle backtesting
            await eval_class_instance.start_evaluator(bot_id)
            return eval_class_instance
    except Exception as e:
        logging.get_logger(LOGGER_NAME).exception(e, True, f"Error when creating evaluator {evaluator_class}: {e}")
    return None


async def create_all_type_evaluators(tentacles_setup_config: object,
                                     matrix_id: str,
                                     exchange_name: str,
                                     bot_id: str,
                                     symbols_by_crypto_currencies: dict = None,
                                     symbols: list = None,
                                     time_frames: list = None,
                                     real_time_time_frames: list = None,
                                     relevant_evaluators=common_constants.CONFIG_WILDCARD,
                                     ) -> list:
    if not api.get_activated_strategies_classes(tentacles_setup_config):
        # If no strategy is activated, there is no evaluator to create (their evaluation would not be used)
        logging.get_logger(LOGGER_NAME).info(
            f"No evaluator to create for {exchange_name}: no activated evaluator strategy.")
        return []
    crypto_currency_name_by_crypto_currencies = {}
    symbols_by_crypto_currency_tickers = {}
    try:
        import octobot_trading.api as exchange_api
        exchange_id = exchange_api.get_exchange_id_from_matrix_id(exchange_name, matrix_id)
        exchange_manager = exchange_api.get_exchange_manager_from_exchange_name_and_id(exchange_name, exchange_id)
        for name, symbol_list in symbols_by_crypto_currencies.items():
            if symbol_list:
                base = exchange_api.get_base_currency(exchange_manager, symbol_list[0])
                crypto_currency_name_by_crypto_currencies[base] = \
                    crypto_currency_name_by_crypto_currencies.get(base, "") + name
                symbols_by_crypto_currency_tickers[base] = \
                    symbols_by_crypto_currency_tickers.get(base, []) + symbol_list
        return [
            await create_evaluators(
                evaluator_type, tentacles_setup_config,
                matrix_id=matrix_id, exchange_name=exchange_name,
                bot_id=bot_id,
                crypto_currency_name_by_crypto_currencies=crypto_currency_name_by_crypto_currencies,
                symbols_by_crypto_currency_tickers=symbols_by_crypto_currency_tickers,
                symbols=symbols, time_frames=time_frames,
                real_time_time_frames=real_time_time_frames,
                relevant_evaluators=relevant_evaluators)
            for evaluator_type in evaluator.EvaluatorClassTypes.values()]
    except ImportError:
        logging.get_logger(LOGGER_NAME).error("create_evaluators requires Octobot-Trading package installed")
    return []
