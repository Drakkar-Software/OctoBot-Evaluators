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
import async_channel.util as channel_util

import octobot_tentacles_manager.api as api

import octobot_commons.constants as common_constants
import octobot_commons.channels_name as channels_name
import octobot_commons.tentacles_management as tentacles_management
import octobot_commons.time_frame_manager as time_frame_manager

import octobot_evaluators.evaluators.channel as evaluator_channels
import octobot_evaluators.constants as constants
import octobot_evaluators.evaluators as evaluator


def init_time_frames_from_strategies(config, tentacles_setup_config) -> None:
    time_frame_list = set()
    for strategies_eval_class in get_activated_strategies_classes(tentacles_setup_config):
        for time_frame in strategies_eval_class.get_required_time_frames(config, tentacles_setup_config):
            time_frame_list.add(time_frame)
    time_frame_list = time_frame_manager.sort_time_frames(list(time_frame_list))
    config[common_constants.CONFIG_TIME_FRAME] = time_frame_list


def get_activated_strategies_classes(tentacles_setup_config):
    return [
        strategies_eval_class
        for strategies_eval_class in tentacles_management.get_all_classes_from_parent(evaluator.StrategyEvaluator)
        if api.is_tentacle_activated_in_tentacles_setup_config(tentacles_setup_config, strategies_eval_class.get_name())
    ]


async def create_evaluator_channels(matrix_id: str, is_backtesting: bool = False) -> None:
    await channel_util.create_all_subclasses_channel(evaluator_channels.EvaluatorChannel,
                                                     evaluator_channels.set_chan,
                                                     is_synchronized=is_backtesting, matrix_id=matrix_id)


def del_evaluator_channels(matrix_id: str) -> None:
    evaluator_channels.del_chan(constants.MATRIX_CHANNEL, matrix_id)
    evaluator_channels.del_chan(constants.EVALUATORS_CHANNEL, matrix_id)


def matrix_channel_exists(matrix_id: str) -> bool:
    try:
        evaluator_channels.get_chan(constants.MATRIX_CHANNEL, matrix_id)
        return True
    except KeyError:
        return False
