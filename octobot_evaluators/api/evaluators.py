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
from octobot_commons.logging.logging_util import get_logger
from octobot_commons.tentacles_management.advanced_manager import AdvancedManager

from octobot_evaluators.api.inspection import is_relevant_evaluator
from octobot_evaluators.enums import EvaluatorMatrixTypes
from octobot_evaluators.evaluator import TAEvaluator, SocialEvaluator, RealTimeEvaluator, StrategyEvaluator

EvaluatorClassTypes = {
    "TA": TAEvaluator,
    "SOCIAL": SocialEvaluator,
    "REAL_TIME": RealTimeEvaluator,
    "STRATEGIES": StrategyEvaluator
}


def create_evaluators(evaluator_parent_class, config, exchange_name,
                      symbol=None, time_frame=None, relevant_evaluators=None) -> list:
    created_evaluators = []
    for eval_class in AdvancedManager.create_advanced_evaluator_types_list(evaluator_parent_class, config):
        try:
            eval_class_instance = eval_class()
            eval_class_instance.config = config
            if not relevant_evaluators or is_relevant_evaluator(eval_class_instance, relevant_evaluators):
                eval_class_instance.set_logger(get_logger(eval_class.get_name()))

                if symbol:
                    eval_class_instance.symbol = symbol

                if time_frame:
                    eval_class_instance.time_frame = time_frame
        except Exception as e:
            get_logger().error(f"Error when creating evaluator {eval_class}: {e}")
            get_logger().exception(e)

    return created_evaluators


def create_all_type_evaluators(config, exchange_name, symbol, time_frame, relevant_evaluators=None) -> list:
    created_evaluators = []

    created_evaluators += create_evaluators(EvaluatorClassTypes[EvaluatorMatrixTypes.TA.value],
                                            config, exchange_name, symbol=symbol, time_frame=time_frame,
                                            relevant_evaluators=relevant_evaluators)

    created_evaluators += create_evaluators(EvaluatorClassTypes[EvaluatorMatrixTypes.SOCIAL.value], config,
                                            exchange_name, relevant_evaluators=relevant_evaluators)

    created_evaluators += create_evaluators(EvaluatorClassTypes[EvaluatorMatrixTypes.REAL_TIME.value], config,
                                            exchange_name, symbol=symbol, relevant_evaluators=relevant_evaluators)

    created_evaluators += create_evaluators(EvaluatorClassTypes[EvaluatorMatrixTypes.STRATEGIES.value],
                                            config, exchange_name, symbol=symbol, time_frame=time_frame,
                                            relevant_evaluators=relevant_evaluators)

    return created_evaluators
