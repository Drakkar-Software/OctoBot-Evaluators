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

from octobot_commons.constants import CONFIG_WILDCARD
from octobot_commons.logging.logging_util import get_logger
from octobot_commons.tentacles_management import create_classes_list, create_advanced_types_list
from octobot_commons.time_frame_manager import get_config_time_frame

from octobot_evaluators.api.initialization import init_time_frames_from_strategies
from octobot_evaluators.api.inspection import is_relevant_evaluator
from octobot_evaluators.constants import EVALUATOR_CLASS_TYPE_MRO_INDEX, evaluator_class_str_to_matrix_type_dict
from octobot_evaluators.data.matrix import Matrix
from octobot_evaluators.enums import EvaluatorMatrixTypes
from octobot_evaluators.evaluator import TAEvaluator, SocialEvaluator, RealTimeEvaluator, StrategyEvaluator, \
    AbstractEvaluator
from octobot_evaluators.evaluator.abstract_util import AbstractUtil
from octobot_evaluators.matrices.matrices import Matrices

EvaluatorClassTypes = {
    EvaluatorMatrixTypes.TA.value: TAEvaluator,
    EvaluatorMatrixTypes.SOCIAL.value: SocialEvaluator,
    EvaluatorMatrixTypes.REAL_TIME.value: RealTimeEvaluator,
    EvaluatorMatrixTypes.STRATEGIES.value: StrategyEvaluator
}


async def create_evaluators(evaluator_parent_class,
                            config: dict,
                            tentacles_setup_config: object,
                            matrix_id: str,
                            exchange_name: str,
                            cryptocurrencies: list = None,
                            symbols: list = None,
                            time_frames: list = None,
                            relevant_evaluators=CONFIG_WILDCARD) -> list:
    return [
        await create_evaluator(evaluator_class, tentacles_setup_config,
                               matrix_id=matrix_id,
                               exchange_name=exchange_name,
                               cryptocurrency=cryptocurrency,
                               symbol=symbol,
                               time_frame=time_frame,
                               relevant_evaluators=relevant_evaluators)
        for evaluator_class in create_advanced_types_list(evaluator_parent_class, config)
        for cryptocurrency in __get_cryptocurrencies_to_create(evaluator_class, cryptocurrencies)
        for symbol in __get_symbols_to_create(evaluator_class, symbols)
        for time_frame in __get_time_frames_to_create(evaluator_class, time_frames)
    ]


def __get_cryptocurrencies_to_create(evaluator_class, cryptocurrencies):  # TODO replace with python 3.8 by :=
    return cryptocurrencies if cryptocurrencies and not evaluator_class.get_is_cryptocurrencies_wildcard() else [None]


def __get_symbols_to_create(evaluator_class, symbols):  # TODO replace with python 3.8 by :=
    return symbols if symbols and not evaluator_class.get_is_symbol_wildcard() else [None]


def __get_time_frames_to_create(evaluator_class, time_frames):  # TODO replace with python 3.8 by :=
    return time_frames if time_frames and not evaluator_class.get_is_time_frame_wildcard() else [None]


async def stop_evaluator(evaluator) -> None:
    return await evaluator.stop()


def get_evaluator_classes_from_type(evaluator_type, config, tentacles_setup_config, activated_only=True) -> list:
    if activated_only:
        return [cls for cls in create_advanced_types_list(EvaluatorClassTypes[evaluator_type], config)
                if cls.is_enabled(tentacles_setup_config, False)]
    return create_advanced_types_list(EvaluatorClassTypes[evaluator_type], config)


async def create_evaluator(evaluator_class,
                           tentacles_setup_config: object,
                           matrix_id: str,
                           exchange_name: str,
                           cryptocurrency: str = None,
                           symbol: str = None,
                           time_frame=None,
                           relevant_evaluators=CONFIG_WILDCARD):
    try:
        eval_class_instance = evaluator_class()
        eval_class_instance.set_tentacles_setup_config(tentacles_setup_config)
        if is_relevant_evaluator(eval_class_instance, relevant_evaluators):
            eval_class_instance.logger = get_logger(evaluator_class.get_name())
            eval_class_instance.matrix_id = matrix_id
            eval_class_instance.exchange_name = exchange_name if exchange_name else None
            eval_class_instance.cryptocurrency = cryptocurrency if cryptocurrency else None
            eval_class_instance.symbol = symbol if symbol else None
            eval_class_instance.time_frame = time_frame if time_frame else None
            eval_class_instance.evaluator_type = evaluator_class_str_to_matrix_type_dict[
                eval_class_instance.__class__.mro()[EVALUATOR_CLASS_TYPE_MRO_INDEX].__name__]
            await eval_class_instance.prepare()

            await eval_class_instance.start_evaluator()
            return eval_class_instance
    except Exception as e:
        get_logger().exception(e, True, f"Error when creating evaluator {evaluator_class}: {e}")
    return None


"""
:param config: evaluator config
:return: initialized matrix id
"""


async def initialize_evaluators(config, tentacles_setup_config) -> str:
    create_evaluator_classes(config)
    _init_time_frames(config, tentacles_setup_config)

    return create_matrix()


def create_evaluator_classes(config):
    create_classes_list(config, AbstractEvaluator)
    create_classes_list(config, AbstractUtil)


def get_evaluators_time_frames(config) -> list:
    return get_config_time_frame(config)


def _init_time_frames(config, tentacles_setup_config) -> list:
    # Init time frames using enabled strategies
    init_time_frames_from_strategies(config, tentacles_setup_config)
    time_frames = copy.copy(get_config_time_frame(config))

    # Init display time frame
    # config_time_frames = get_config_time_frame(config)

    # if TimeFrames.ONE_HOUR not in config_time_frames and not backtesting_enabled(config):
    #     config_time_frames.append(TimeFrames.ONE_HOUR)
    #     sort_config_time_frames(config)

    return time_frames


def create_matrix() -> str:
    created_matrix: Matrix = Matrix()
    Matrices.instance().add_matrix(created_matrix)
    return created_matrix.id


async def create_all_type_evaluators(config: dict,
                                     tentacles_setup_config: object,
                                     matrix_id: str,
                                     exchange_name: str,
                                     cryptocurrencies: str = None,
                                     symbols: str = None,
                                     time_frames=None,
                                     relevant_evaluators=CONFIG_WILDCARD) -> list:
    return [await create_evaluators(evaluator_type, config, tentacles_setup_config,
                                    matrix_id=matrix_id, exchange_name=exchange_name,
                                    symbols=symbols, time_frames=time_frames,
                                    cryptocurrencies=cryptocurrencies, relevant_evaluators=relevant_evaluators)
            for evaluator_type in EvaluatorClassTypes.values()]
