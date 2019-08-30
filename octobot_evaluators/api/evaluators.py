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
                            symbol=None, time_frame=None, relevant_evaluators=None) -> list:
    created_evaluators = []
    for eval_class in create_advanced_types_list(evaluator_parent_class, config):
        try:
            eval_class_instance = eval_class()
            eval_class_instance.set_config(config)
            if not relevant_evaluators or is_relevant_evaluator(eval_class_instance, relevant_evaluators):
                eval_class_instance.logger = get_logger(eval_class.get_name())

                if symbol:
                    eval_class_instance.symbol = symbol

                if exchange_name:
                    eval_class_instance.exchange_name = exchange_name

                if time_frame:
                    eval_class_instance.time_frame = time_frame

                await eval_class_instance.start_evaluator()
        except Exception as e:
            get_logger().error(f"Error when creating evaluator {eval_class}: {e}")
            get_logger().exception(e)

    return created_evaluators


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
    config_time_frames = TimeFrameManager.get_config_time_frame(config)

    # if TimeFrames.ONE_HOUR not in config_time_frames and not backtesting_enabled(config):
    #     config_time_frames.append(TimeFrames.ONE_HOUR)
    #     TimeFrameManager.sort_config_time_frames(config)

    return time_frames


async def create_all_type_evaluators(config, exchange_name, symbol, time_frame, relevant_evaluators=None) -> list:
    created_evaluators = []

    created_evaluators += await create_evaluators(EvaluatorClassTypes[EvaluatorMatrixTypes.TA.value],
                                                  config, exchange_name, symbol=symbol, time_frame=time_frame,
                                                  relevant_evaluators=relevant_evaluators)

    created_evaluators += await create_evaluators(EvaluatorClassTypes[EvaluatorMatrixTypes.SOCIAL.value], config,
                                                  exchange_name, relevant_evaluators=relevant_evaluators)

    created_evaluators += await create_evaluators(EvaluatorClassTypes[EvaluatorMatrixTypes.REAL_TIME.value], config,
                                                  exchange_name, symbol=symbol, relevant_evaluators=relevant_evaluators)

    created_evaluators += await create_evaluators(EvaluatorClassTypes[EvaluatorMatrixTypes.STRATEGIES.value],
                                                  config, exchange_name, symbol=symbol, time_frame=time_frame,
                                                  relevant_evaluators=relevant_evaluators)

    return created_evaluators
