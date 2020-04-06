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

from octobot_commons.constants import CONFIG_WILDCARD
from octobot_commons.tentacles_management.advanced_manager import create_advanced_types_list

from octobot_evaluators.evaluator import StrategyEvaluator, TAEvaluator


def get_relevant_evaluators_from_strategies(config, tentacles_setup_config) -> list:
    evaluator_list = set()
    for strategies_eval_class in create_advanced_types_list(StrategyEvaluator, config):
        if strategies_eval_class.is_enabled(tentacles_setup_config, False):
            required_evaluators = strategies_eval_class.get_required_evaluators(config)
            if required_evaluators == CONFIG_WILDCARD:
                return CONFIG_WILDCARD
            else:
                for evaluator in required_evaluators:
                    evaluator_list.add(evaluator)
    return evaluator_list


def is_relevant_evaluator(evaluator_instance, relevant_evaluators) -> bool:
    if evaluator_instance.enabled:
        if relevant_evaluators == CONFIG_WILDCARD or \
                evaluator_instance.get_name() in relevant_evaluators:
            return True
        else:
            parent_classes_names = [e.get_name() for e in evaluator_instance.get_parent_evaluator_classes()]
            to_check_set = relevant_evaluators
            if not isinstance(relevant_evaluators, set):
                to_check_set = set(relevant_evaluators)
            return not to_check_set.isdisjoint(parent_classes_names)
    return False


def get_relevant_TAs_for_strategy(strategy, config, tentacles_setup_config) -> list:
    ta_classes_list = []
    relevant_evaluators = strategy.get_required_evaluators(config)
    for ta_eval_class in create_advanced_types_list(TAEvaluator, config):
        ta_eval_class_instance = ta_eval_class()
        ta_eval_class_instance.set_tentacles_setup_config(tentacles_setup_config)
        if CONFIG_WILDCARD in relevant_evaluators or \
                is_relevant_evaluator(ta_eval_class_instance, relevant_evaluators):
            ta_classes_list.append(ta_eval_class)
    return ta_classes_list
