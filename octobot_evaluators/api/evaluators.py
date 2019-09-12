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
import copy

from octobot_commons.constants import CONFIG_EVALUATOR_FILE_PATH
from octobot_commons.errors import ConfigEvaluatorError
from octobot_commons.logging.logging_util import get_logger
from octobot_commons.tentacles_management import create_classes_list, create_advanced_types_list
from octobot_commons.tentacles_management.config_manager import reload_tentacle_config
from octobot_commons.time_frame_manager import TimeFrameManager

from octobot_evaluators.api.initialization import init_time_frames_from_strategies
from octobot_evaluators.api.inspection import is_relevant_evaluator
from octobot_evaluators.constants import CONFIG_EVALUATOR
from octobot_evaluators.enums import EvaluatorMatrixTypes
from octobot_evaluators.evaluator import TAEvaluator, SocialEvaluator, RealTimeEvaluator, StrategyEvaluator, \
    AbstractEvaluator
from octobot_evaluators.evaluator.abstract_util import AbstractUtil

EvaluatorClassTypes = {
    "TA": TAEvaluator,
    "SOCIAL": SocialEvaluator,
    "REAL_TIME": RealTimeEvaluator,
    "STRATEGIES": StrategyEvaluator
}


async def create_evaluators(evaluator_parent_class, config, exchange_name,
                            symbols=None, time_frames=None, relevant_evaluators=None) -> list:
    return [
        await create_evaluator(evaluator_class, config, exchange_name,
                               symbol=symbol,
                               time_frame=time_frame,
                               relevant_evaluators=relevant_evaluators)
        for evaluator_class in create_advanced_types_list(evaluator_parent_class, config)
        for symbol in __get_symbols_to_create(evaluator_class, symbols)
        for time_frame in __get_time_frames_to_create(evaluator_class, time_frames)
    ]


def __get_symbols_to_create(evaluator_class, symbols):  # TODO replace with python 3.8 by :=
    return symbols if symbols and not evaluator_class.get_is_symbol_widlcard() else [None]


def __get_time_frames_to_create(evaluator_class, time_frames):  # TODO replace with python 3.8 by :=
    return time_frames if time_frames and not evaluator_class.get_is_time_frame_widlcard() else [None]


async def create_evaluator(evaluator_class, config, exchange_name,
                           symbol=None,
                           time_frame=None,
                           relevant_evaluators=None):
    try:
        eval_class_instance = evaluator_class()
        eval_class_instance.set_config(config)
        if not relevant_evaluators or is_relevant_evaluator(eval_class_instance, relevant_evaluators):
            eval_class_instance.logger = get_logger(evaluator_class.get_name())
            eval_class_instance.exchange_name = exchange_name if exchange_name else None
            eval_class_instance.symbol = symbol if symbol else None
            eval_class_instance.time_frame = time_frame if time_frame else None

            await eval_class_instance.start_evaluator()
            return eval_class_instance
    except Exception as e:
        get_logger().error(f"Error when creating evaluator {evaluator_class}: {e}")
        get_logger().exception(e)
    return None


async def initialize_evaluators(config) -> None:
    reload_tentacle_config(config, CONFIG_EVALUATOR, CONFIG_EVALUATOR_FILE_PATH, ConfigEvaluatorError)

    create_classes_list(config, AbstractEvaluator)
    create_classes_list(config, AbstractUtil)

    __init_time_frames(config)


def __init_time_frames(config) -> list:
    # Init time frames using enabled strategies
    init_time_frames_from_strategies(config)
    time_frames = copy.copy(TimeFrameManager.get_config_time_frame(config))

    # Init display time frame
    # config_time_frames = TimeFrameManager.get_config_time_frame(config)

    # if TimeFrames.ONE_HOUR not in config_time_frames and not backtesting_enabled(config):
    #     config_time_frames.append(TimeFrames.ONE_HOUR)
    #     TimeFrameManager.sort_config_time_frames(config)

    return time_frames


async def create_all_type_evaluators(config, exchange_name, symbols, time_frames, relevant_evaluators=None) -> list:
    created_evaluators = []

    created_evaluators += await create_evaluators(EvaluatorClassTypes[EvaluatorMatrixTypes.TA.value],
                                                  config, exchange_name, symbols=symbols, time_frames=time_frames,
                                                  relevant_evaluators=relevant_evaluators)

    created_evaluators += await create_evaluators(EvaluatorClassTypes[EvaluatorMatrixTypes.SOCIAL.value], config,
                                                  exchange_name, relevant_evaluators=relevant_evaluators)

    created_evaluators += await create_evaluators(EvaluatorClassTypes[EvaluatorMatrixTypes.REAL_TIME.value],
                                                  config, exchange_name, symbols=symbols,
                                                  relevant_evaluators=relevant_evaluators)

    created_evaluators += await create_evaluators(EvaluatorClassTypes[EvaluatorMatrixTypes.STRATEGIES.value],
                                                  config, exchange_name, symbols=symbols, time_frames=time_frames,
                                                  relevant_evaluators=relevant_evaluators)

    return created_evaluators
