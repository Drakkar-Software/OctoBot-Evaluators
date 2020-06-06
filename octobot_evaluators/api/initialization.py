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
from octobot_channels.util.channel_creator import create_all_subclasses_channel
from octobot_commons.constants import CONFIG_TIME_FRAME
from octobot_commons.tentacles_management.class_inspector import get_all_classes_from_parent
from octobot_commons.time_frame_manager import sort_time_frames
from octobot_evaluators.channels.evaluator_channel import get_chan, set_chan, EvaluatorChannel, del_chan
from octobot_evaluators.constants import MATRIX_CHANNEL
from octobot_evaluators.evaluator import StrategyEvaluator, EVALUATORS_CHANNEL
from octobot_tentacles_manager.api.configurator import is_tentacle_activated_in_tentacles_setup_config


def init_time_frames_from_strategies(config, tentacles_setup_config) -> None:
    time_frame_list = set()
    for strategies_eval_class in get_activated_strategies_classes(tentacles_setup_config):
        for time_frame in strategies_eval_class.get_required_time_frames(config):
            time_frame_list.add(time_frame)
    time_frame_list = sort_time_frames(list(time_frame_list))
    config[CONFIG_TIME_FRAME] = time_frame_list


def get_activated_strategies_classes(tentacles_setup_config):
    return [
        strategies_eval_class
        for strategies_eval_class in get_all_classes_from_parent(StrategyEvaluator)
        if is_tentacle_activated_in_tentacles_setup_config(tentacles_setup_config, strategies_eval_class.get_name())
    ]


async def create_evaluator_channels(matrix_id: str, is_backtesting: bool = False) -> None:
    await create_all_subclasses_channel(EvaluatorChannel, set_chan, is_synchronized=is_backtesting, matrix_id=matrix_id)


def del_evaluator_channels(matrix_id: str) -> None:
    del_chan(MATRIX_CHANNEL, matrix_id)
    del_chan(EVALUATORS_CHANNEL, matrix_id)


def matrix_channel_exists(matrix_id: str) -> bool:
    try:
        get_chan(MATRIX_CHANNEL, matrix_id)
        return True
    except KeyError:
        return False
